#!/usr/bin/env python3
"""Public, read-only market-data collector. Never accesses trading endpoints.
GitHub secrets: ALPACA_API_KEY_ID / ALPACA_API_SECRET_KEY.
Output: docs/precios.json and docs/lectura_rapida.md (public, no credentials).
"""
from __future__ import annotations
import csv
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'docs'
NASDAQ = 'https://api.nasdaq.com/api/screener/stocks?download=true&limit=25&offset=0&tableonly=true'
ALPACA = 'https://data.alpaca.markets/v2/stocks/snapshots'
USER_AGENT = 'Mozilla/5.0 (compatible; MarketResearchBot/1.0)'
STAMP = dt.timezone.utc


def utcnow():
    return dt.datetime.now(STAMP)


def iso(t):
    return t.isoformat(timespec='seconds').replace('+00:00', 'Z')


def parse_time(raw):
    if not raw:
        return None
    try:
        return dt.datetime.fromisoformat(str(raw).replace('Z', '+00:00')).astimezone(STAMP)
    except (ValueError, TypeError):
        return None


def numeric(raw):
    if raw is None: return None
    try:
        n = float(re.sub(r'[$,%\s,]', '', str(raw)))
        return n if n == n and abs(n) != float('inf') else None
    except (ValueError, TypeError):
        return None


def valid_symbol(raw):
    s = str(raw or '').strip().upper()
    return s if re.fullmatch(r'[A-Z][A-Z0-9.\-]{0,11}', s) else None


def request_json(url, headers=None, attempts=2, timeout=24):
    req = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'application/json', **(headers or {})})
    err = None
    for i in range(attempts):
        try:
            with urlopen(req, timeout=timeout) as response:
                return json.load(response)
        except (HTTPError, URLError, TimeoutError, ValueError) as e:
            err = e
            if isinstance(e, HTTPError) and e.code not in (429, 500, 502, 503, 504):
                break
            if i + 1 < attempts: time.sleep(1.5 * (i + 1))
    raise RuntimeError(f'Fuente inaccesible ({type(err).__name__}, codigo={getattr(err, "code", "n/a")})')


def base_symbols():
    with (ROOT / 'universo_fintual_publico.csv').open(encoding='utf-8-sig', newline='') as f:
        symbols = {valid_symbol(row['symbol']) for row in csv.DictReader(f)}
    symbols.discard(None)
    priority = []
    for raw in (ROOT / 'prioridad.txt').read_text(encoding='utf-8').splitlines():
        s = valid_symbol(raw.split('#')[0])
        if s and s in symbols and s not in priority:
            priority.append(s)
    return symbols, priority


def pick_symbols(nasdaq_rows, universe, priority, max_symbols=70):
    candidates = []
    overlap = 0
    for r in nasdaq_rows:
        s = valid_symbol(r.get('symbol'))
        if not s or s not in universe:
            continue
        overlap += 1
        price, volume, pct = numeric(r.get('lastsale')), numeric(r.get('volume')), numeric(r.get('pctchange'))
        # Source screener timestamps can be absent; these values only select symbols.
        if not (price and price > 0.5 and volume and volume >= 100000 and pct is not None and abs(pct) >= 3):
            continue
        notional = price * volume
        if notional < 5_000_000: continue
        candidates.append({'symbol': s, 'pctchange_unverified': pct, 'notional_proxy': round(notional, 2), 'sector': r.get('sector')})
    candidates.sort(key=lambda x: (-abs(x['pctchange_unverified']), -x['notional_proxy']))
    chosen = list(priority)
    for r in candidates:
        if r['symbol'] not in chosen and len(chosen) < max_symbols:
            chosen.append(r['symbol'])
    return chosen[:max_symbols], overlap, candidates


def extract_snapshots(payload, requested, now):
    result = []
    for sym in requested:
        snap = payload.get(sym) or {}
        trade, quote = snap.get('latestTrade') or {}, snap.get('latestQuote') or {}
        t, q = parse_time(trade.get('t')), parse_time(quote.get('t'))
        trade_age = round((now-t).total_seconds(), 1) if t else None
        quote_age = round((now-q).total_seconds(), 1) if q else None
        bp, ap = numeric(quote.get('bp')), numeric(quote.get('ap'))
        spread = round(100 * (ap-bp)/((ap+bp)/2), 3) if bp and ap and ap>=bp else None
        recent_trade = trade_age is not None and 0 <= trade_age <= 120
        recent_quote = quote_age is not None and 0 <= quote_age <= 60
        result.append({
            'symbol': sym,
            'last_trade_usd': numeric(trade.get('p')),
            'last_trade_utc': iso(t) if t else None,
            'last_trade_age_sec': trade_age,
            'bid_iex_usd': bp,
            'ask_iex_usd': ap,
            'last_quote_utc': iso(q) if q else None,
            'last_quote_age_sec': quote_age,
            'spread_iex_pct': spread,
            'recent_trade_120sec': recent_trade,
            'recent_quote_60sec': recent_quote,
            'research_only_not_fintual_verified': True,
        })
    return result


def fetch_alpaca(symbols, key, secret, now):
    data = {}
    headers = {'APCA-API-KEY-ID': key, 'APCA-API-SECRET-KEY': secret}
    failures=[]
    for start in range(0, len(symbols), 35):
        chunk = symbols[start:start+35]
        url = ALPACA + '?' + urlencode({'symbols': ','.join(chunk), 'feed': 'iex'})
        try:
            payload = request_json(url, headers, attempts=2)
            data.update({s: payload.get(s) for s in chunk if isinstance(payload.get(s), dict)})
        except RuntimeError as exc:
            failures.append(f'Lote {start//35+1}: {exc}')
        if start + 35 < len(symbols): time.sleep(.5)
    return extract_snapshots(data, symbols, now), failures


def render_markdown(report):
    a = report['audit']
    lines = [
        '# Fintual × Nasdaq × Alpaca: actualización automática',
        '', f"**Extracción (UTC):** {report['generated_at_utc']}",
        f"**Hora NY:** {report['generated_at_new_york']}",
        f"**Estado:** {report['status']}",
        '', '**Alcance real de esta ejecución:**',
        f"- Base pública histórica Fintual (símbolos): {a['public_fintual_symbols']}; NO prueba disponibilidad en la app.",
        f"- Filas Nasdaq descargadas: {a['nasdaq_rows_processed'] if a['nasdaq_rows_processed'] is not None else 'NO VERIFICABLE'}; frescura Nasdaq NO VERIFICABLE cuando asOf=null.",
        f"- Coincidencias Nasdaq-base Fintual: {a['nasdaq_fintual_matches'] if a['nasdaq_fintual_matches'] is not None else 'NO VERIFICABLE'}.",
        f"- Símbolos IEX solicitados: {a['iex_symbols_requested']}; con operación y cotización recientes: {a['iex_recent_trade_and_quote']}. IEX no es SIP consolidado.",
        '', '| Ticker | Último IEX USD | Hora operación UTC | Edad seg. | Bid | Ask | Spread IEX | Dato reciente |',
        '|---|---:|---|---:|---:|---:|---:|---|',
    ]
    for r in report['prices']:
        fmt=lambda k: f"{r[k]:.3f}" if isinstance(r.get(k),(int,float)) else '—'
        recent = 'SÍ' if r['recent_trade_120sec'] and r['recent_quote_60sec'] else 'NO'
        lines.append(f"| {r['symbol']} | {fmt('last_trade_usd')} | {r.get('last_trade_utc') or '—'} | {fmt('last_trade_age_sec')} | {fmt('bid_iex_usd')} | {fmt('ask_iex_usd')} | {fmt('spread_iex_pct')} | {recent} |")
    lines += [
        '', '> **NO SON ÓRDENES DE COMPRA.** Solo una bolsa (IEX), no precios consolidados. No usar un spread IEX aislado como spread del mercado.',
        '> Ninguna coincidencia pública demuestra que la acción esté habilitada en el contrato personal de Fintual.',
        '> Comprobar en Fintual el precio real y las condiciones antes de operar.',
    ]
    if a['warnings']: lines += ['', '**Advertencias:**'] + [f'- {x}' for x in a['warnings']]
    return '\n'.join(lines) + '\n'


def build_report(universe, priority, nasdaq_payload, snap_payload, now):
    """Pure aggregation helper used by local tests."""
    nasa = nasdaq_payload.get('data') or {}
    rows = nasa.get('rows') or []
    chosen, overlap, screened = pick_symbols(rows, universe, priority)
    snapshots = extract_snapshots(snap_payload, chosen, now)
    return chosen, overlap, screened, snapshots


def main():
    key, secret = os.getenv('ALPACA_API_KEY_ID'), os.getenv('ALPACA_API_SECRET_KEY')
    if not key or not secret:
        raise SystemExit('Faltan secretos de GitHub: ALPACA_API_KEY_ID y ALPACA_API_SECRET_KEY (no pegar valores en el repositorio).')
    now=utcnow()
    universe, priority=base_symbols()
    nasdaq_rows=[]; asof=None; nerror=None
    try:
        payload=request_json(NASDAQ, attempts=2)
        data=payload.get('data') or {}
        nasdaq_rows=data.get('rows') or []
        if not isinstance(nasdaq_rows, list):
            raise ValueError('data.rows no es una lista')
        asof=data.get('asOf')
    except (RuntimeError, ValueError, AttributeError) as exc:
        nerror=f'Nasdaq no disponible: {type(exc).__name__}'
        nasdaq_rows=[]
    chosen, overlap, screened=pick_symbols(nasdaq_rows, universe, priority)
    quotes, qerrors=fetch_alpaca(chosen,key,secret,now)
    recent=sum(bool(x['recent_trade_120sec'] and x['recent_quote_60sec']) for x in quotes)
    quote_rows=sum(bool(x['last_trade_utc'] or x['last_quote_utc']) for x in quotes)
    warnings=[]
    if nerror: warnings.append(nerror+'; se usó la lista prioritaria.')
    if asof is None: warnings.append('Nasdaq asOf nulo/ausente: hora de precios masivos no verificable; sus cifras solo seleccionan símbolos.')
    warnings += qerrors
    if quote_rows == 0: warnings.append('Ninguna cotización IEX fechada disponible: NO OPERAR sobre este archivo.')
    audit={
        'public_fintual_symbols':len(universe),
        'fintual_catalog_complete_2026':False,
        'user_contract_tradability_confirmed':False,
        'nasdaq_rows_processed':len(nasdaq_rows) if nasdaq_rows else None,
        'nasdaq_asof':asof,
        'nasdaq_fintual_matches':overlap if nasdaq_rows else None,
        'quantitative_filter_passed':len(screened) if nasdaq_rows else None,
        'iex_symbols_requested':len(chosen),
        'iex_symbols_with_timestamp':quote_rows,
        'iex_recent_trade_and_quote':recent,
        'iex_batch_errors':len(qerrors),
        'warnings':warnings,
    }
    status='OK_PARCIAL_RESEARCH_ONLY' if recent and not qerrors else 'INCOMPLETE_NO_TRADE'
    report={
        'generated_at_utc':iso(now),
        'generated_at_new_york':now.astimezone(ZoneInfo('America/New_York')).isoformat(timespec='seconds'),
        'status':status,
        'feed':'IEX only, not consolidated SIP',
        'market_data_excludes_trade_execution':True,
        'audit':audit,
        'prices':quotes,
    }
    OUT.mkdir(exist_ok=True)
    (OUT/'precios.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    (OUT/'lectura_rapida.md').write_text(render_markdown(report), encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('generated_at_utc','status','feed')},ensure_ascii=False))
    print('Nasdaq:',audit['nasdaq_rows_processed'],'IEX:',audit['iex_symbols_requested'],'con datos recientes:',recent)
    return 0 if quote_rows else 2

if __name__=='__main__':
    sys.exit(main())
