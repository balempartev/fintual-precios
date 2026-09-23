#!/usr/bin/env python3
"""Read-only market radar; fail closed on public repositories."""
from __future__ import annotations

import csv
import datetime as dt
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import fuentes_primarias as primary

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
NY = ZoneInfo("America/New_York")
UTC = dt.timezone.utc
CATALOG, STATUS, PRICES = (DOCS / name for name in ("catalogo.json", "estado.json", "precios.json"))
NASDAQ_FILES = (
    "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt",
    "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt",
)
FINTUAL = "https://ayuda.fintual.cl/es/articles/8592794-todas-las-acciones-etfs-disponibles-en-fintual"
SEC_TICKERS = "https://www.sec.gov/files/company_tickers.json"
ALPACA = "https://data.alpaca.markets/v2/stocks/snapshots"
CHUNK = 75
USER_AGENT = "RadarFintual/1.0 balempartev@users.noreply.github.com"


def now_utc():
    return dt.datetime.now(UTC)


def iso(value):
    return value.astimezone(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_time(value):
    if not value:
        return None
    try:
        result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return result.astimezone(UTC) if result.tzinfo else None
    except (TypeError, ValueError):
        return None


def valid_symbol(value):
    s = str(value or "").strip().upper()
    return s if re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,11}", s) else None


def get_bytes(url, headers=None, attempts=2, timeout=18):
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*", **(headers or {})})
    last_error = None
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if isinstance(exc, HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                break
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{urlparse(url).netloc}: {type(last_error).__name__} ({getattr(last_error, 'code', 'n/a')})")


def get_json(url, headers=None, **kwargs):
    return json.loads(get_bytes(url, headers, **kwargs))


class FintualLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.symbols = set()

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href", "")
            match = re.search(r"(?:https?://(?:www\.)?fintual\.cl)?/f/acciones/([a-z0-9.\-]+)/?(?:[?#]|$)", href, re.I)
            if match and (symbol := valid_symbol(match.group(1))):
                self.symbols.add(symbol)


def parse_directory(body, filename):
    rows = csv.DictReader(body.decode("utf-8-sig").splitlines(), delimiter="|")
    result = {}
    for row in rows:
        symbol = valid_symbol(row.get("Symbol") or row.get("ACT Symbol"))
        if not symbol or row.get("Test Issue") != "N":
            continue
        name = row.get("Security Name", "")
        etf = row.get("ETF") == "Y"
        if not etf and re.search(r"\b(warrants?|rights?|units?|preferred|notes?|bonds?|debentures?)\b", name, re.I):
            continue
        exchange = "NASDAQ" if filename == "nasdaqlisted.txt" else {
            "N": "NYSE", "A": "NYSE_AMERICAN", "P": "NYSE_ARCA", "Z": "BATS", "V": "IEX"
        }.get(row.get("Exchange"), "OTHER")
        result[symbol] = {"symbol": symbol, "exchange": exchange, "kind": "ETF" if etf else "EQUITY_CANDIDATE"}
    return result


def historical_symbols():
    with (ROOT / "universo_fintual_publico.csv").open(encoding="utf-8-sig", newline="") as file:
        return {s for row in csv.DictReader(file) if (s := valid_symbol(row.get("symbol")))}


def priority_symbols():
    return [s for line in (ROOT / "prioridad.txt").read_text(encoding="utf-8").splitlines()
            if (s := valid_symbol(line.split("#")[0]))]


def load_catalog():
    try:
        cached = json.loads(CATALOG.read_text(encoding="utf-8"))
        return cached if isinstance(cached["assets"], list) else None
    except (FileNotFoundError, KeyError, ValueError):
        return None


def refresh_catalog(cached, date):
    if cached and cached.get("schema_version") == 2 and cached.get("checked_on_ny") == date and cached.get("directory_complete") and cached.get("fintual_evidence_current"):
        return cached
    sources, warnings, assets = {}, [], {}
    for url in NASDAQ_FILES:
        name = url.rsplit("/", 1)[-1]
        try:
            rows = parse_directory(get_bytes(url), name)
            if len(rows) < 1000:
                raise ValueError("directory too small")
            sources[name] = len(rows)
            assets.update(rows)
        except (RuntimeError, ValueError, UnicodeError) as exc:
            warnings.append(f"Directory {name}: {type(exc).__name__}")
    directory_complete = len(sources) == 2 and len(assets) >= 6000
    if not directory_complete or len(assets) < 6000:
        if cached and len(cached["assets"]) >= 6000:
            return {**cached, "warnings": warnings + ["Retained previous complete directory."]}
        assets = {s: {"symbol": s, "exchange": "UNKNOWN", "kind": "UNKNOWN"} for s in historical_symbols()}
        warnings.append("Only partial historical Fintual list available; broad scan unavailable.")
    try:
        parser = FintualLinks()
        parser.feed(get_bytes(FINTUAL).decode("utf-8"))
        if len(parser.symbols) < 1500:
            raise ValueError("too few Fintual links")
        verified = parser.symbols
        fintual_current = True
        sources["fintual_help_links"] = len(verified)
    except (RuntimeError, ValueError, UnicodeError) as exc:
        verified = set(cached.get("fintual_verified", [])) if cached else set()
        fintual_current = False
        warnings.append(f"Fintual links: {type(exc).__name__}; previous evidence retained.")
    for symbol in verified - assets.keys():
        assets[symbol] = {"symbol": symbol, "exchange": "NOT_IN_CURRENT_DIRECTORY", "kind": "FINTUAL_LINK_ONLY"}
    return {"schema_version": 2, "checked_on_ny": date, "directory_complete": directory_complete,
            "fintual_evidence_current": fintual_current,
            "directory_fetched_at_utc": iso(now_utc()) if directory_complete else (cached or {}).get("directory_fetched_at_utc"),
            "fintual_source": FINTUAL, "sources": sources, "warnings": warnings,
            "fintual_verified": sorted(verified),
            "assets": sorted(assets.values(), key=lambda row: row["symbol"])}


def parse_snapshot(symbol, snapshot, finished):
    trade, quote = snapshot.get("latestTrade") or {}, snapshot.get("latestQuote") or {}
    day, previous = snapshot.get("dailyBar") or {}, snapshot.get("prevDailyBar") or {}
    trade_time, quote_time = parse_time(trade.get("t")), parse_time(quote.get("t"))
    age = round((finished - trade_time).total_seconds(), 1) if trade_time else None
    quote_age = round((finished - quote_time).total_seconds(), 1) if quote_time else None
    price, prior = trade.get("p"), previous.get("c")
    price = price if isinstance(price, (float, int)) and price > 0 else None
    prior = prior if isinstance(prior, (float, int)) and prior > 0 else None
    recent = age is not None and 0 <= age <= 150
    change = round(100 * (price / prior - 1), 3) if recent and price and prior else None
    volume = day.get("v") if isinstance(day.get("v"), (int, float)) else None
    prev_volume = previous.get("v") if isinstance(previous.get("v"), (int, float)) else None
    local = finished.astimezone(NY)
    elapsed = max(1 / 78, min(1., ((local.hour - 9) * 60 + local.minute - 30) / 390))
    proxy = round(volume / (prev_volume * elapsed), 2) if recent and volume is not None and prev_volume and prev_volume > 0 else None
    return {"symbol": symbol, "trade_utc": iso(trade_time) if trade_time else None,
            "trade_age_sec": age, "quote_utc": iso(quote_time) if quote_time else None,
            "quote_age_sec": quote_age, "recent_trade_150sec": recent,
            "recent_quote_60sec": quote_age is not None and 0 <= quote_age <= 60,
            "price_iex_usd": price, "previous_close_iex_usd": prior, "change_iex_pct": change,
            "volume_iex_today": volume, "volume_iex_prev_day": prev_volume,
            "volume_activity_proxy_iex": proxy, "bid_iex_usd": quote.get("bp"), "ask_iex_usd": quote.get("ap")}


def fetch_snapshots(symbols, key, secret):
    headers = {"APCA-API-KEY-ID": key, "APCA-API-SECRET-KEY": secret}
    results, errors = {}, []
    for offset in range(0, len(symbols), CHUNK):
        batch = symbols[offset:offset + CHUNK]
        try:
            payload = get_json(ALPACA + "?" + urlencode({"symbols": ",".join(batch), "feed": "iex"}), headers)
            if not isinstance(payload, dict):
                raise ValueError("response not a dict")
            finished = now_utc()  # Capture after request, never before it.
            for symbol in batch:
                if isinstance(payload.get(symbol), dict):
                    results[symbol] = parse_snapshot(symbol, payload[symbol], finished)
        except (RuntimeError, ValueError) as exc:
            errors.append({"batch_start": offset, "size": len(batch), "error": type(exc).__name__})
        if offset + CHUNK < len(symbols):
            time.sleep(.35)
    return results, errors


def choose_movers(rows, priority, limit=100):
    usable = [row for row in rows.values() if row["change_iex_pct"] is not None]
    up = sorted((row for row in usable if row["change_iex_pct"] > 0), key=lambda row: row["change_iex_pct"], reverse=True)
    down = sorted((row for row in usable if row["change_iex_pct"] < 0), key=lambda row: row["change_iex_pct"])
    volume = sorted((row for row in usable if row["volume_activity_proxy_iex"] is not None),
                    key=lambda row: row["volume_activity_proxy_iex"], reverse=True)
    selected = dict.fromkeys([row["symbol"] for row in up[:limit // 3] + down[:limit // 3] + volume[:limit // 3]] + list(priority))
    return {"gainers": [row["symbol"] for row in up[:20]],
            "losers": [row["symbol"] for row in down[:20]],
            "volume_activity": [row["symbol"] for row in volume[:20] if row["volume_activity_proxy_iex"] >= 2],
            "selected": [rows[s] for s in selected if s in rows]}


def finalize_freshness(rows, finished):
    """All published ages are relative to publication, including early batches."""
    for row in rows.values():
        trade, quote = parse_time(row["trade_utc"]), parse_time(row["quote_utc"])
        row["trade_age_sec"] = round((finished - trade).total_seconds(), 1) if trade else None
        row["quote_age_sec"] = round((finished - quote).total_seconds(), 1) if quote else None
        row["recent_trade_150sec"] = row["trade_age_sec"] is not None and 0 <= row["trade_age_sec"] <= 150
        row["recent_quote_60sec"] = row["quote_age_sec"] is not None and 0 <= row["quote_age_sec"] <= 60
        if not row["recent_trade_150sec"]:
            row["change_iex_pct"] = None
            row["volume_activity_proxy_iex"] = None


def sec_filings(symbols):
    """Links to primary filings; their presence does not prove causation."""
    try:
        tickers = get_json(SEC_TICKERS, attempts=1, timeout=6)
        index = {valid_symbol(v.get("ticker")): int(v["cik_str"]) for v in tickers.values() if valid_symbol(v.get("ticker"))}
    except (RuntimeError, ValueError, TypeError, KeyError) as exc:
        detail = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        index = {"AAPL": 320193, "MSFT": 789019, "NVDA": 1045810}
        mapping_warning = f"SEC ticker mapping unavailable: {detail}; limited CIK seed fallback only"
    else:
        mapping_warning = None
    found, warnings = [], [mapping_warning] if mapping_warning else []
    cutoff = now_utc() - dt.timedelta(days=2)
    for symbol in list(dict.fromkeys(symbols))[:12]:
        if not (cik := index.get(symbol)):
            continue
        try:
            submission = get_json(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", attempts=1, timeout=6)
            if symbol not in submission.get("tickers", []):
                warnings.append(f"SEC ticker/CIK mismatch for {symbol}")
                continue
            recent = submission["filings"]["recent"]
            for form, accepted, accession, document in zip(
                recent["form"], recent["acceptanceDateTime"], recent["accessionNumber"], recent["primaryDocument"]
            ):
                if form not in {"8-K", "6-K", "10-Q", "10-K", "S-1", "S-3", "424B5", "424B3", "F-3"}:
                    continue
                when = parse_time(accepted)
                if when is None:
                    warnings.append(f"SEC ambiguous acceptance timezone for {symbol}")
                    continue
                if when >= cutoff:
                    found.append({"symbol": symbol, "form": form, "accepted_utc": iso(when),
                                  "url": f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{document}"})
                else:
                    break
        except (RuntimeError, ValueError, KeyError, TypeError):
            warnings.append(f"SEC unavailable for {symbol}")
        time.sleep(.15)
    return found[:30], warnings


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")


def run():
    started = now_utc()
    date = started.astimezone(NY).date().isoformat()
    catalog = refresh_catalog(load_catalog(), date)
    assets = {row["symbol"]: row for row in catalog["assets"]}
    priority = list(dict.fromkeys(priority_symbols() + list(primary.SECTORS)))
    symbols = [s for s in assets if s not in priority] + [s for s in priority if s in assets]
    key, secret = os.getenv("ALPACA_API_KEY_ID"), os.getenv("ALPACA_API_SECRET_KEY")
    warnings = list(catalog["warnings"])
    snapshots, errors = fetch_snapshots(symbols, key, secret) if key and secret else ({}, [{"error": "MISSING_CREDENTIALS"}])
    if snapshots:
        shortlist = [row["symbol"] for row in choose_movers(snapshots, priority)["selected"]]
        refreshed, refresh_errors = fetch_snapshots(shortlist, key, secret)
        snapshots.update(refreshed)
        errors += refresh_errors
    finished = now_utc()
    finalize_freshness(snapshots, finished)
    movers = choose_movers(snapshots, priority)
    private = os.getenv("GITHUB_REPOSITORY_PRIVATE", "").lower() == "true"
    filings, filing_warnings = sec_filings([row["symbol"] for row in movers["selected"][:12]] if private else priority)
    warnings.extend(filing_warnings)
    news = primary.collect(get_bytes, now_utc())
    write_json(DOCS / "catalizadores.json", news)
    finished = now_utc()
    finalize_freshness(snapshots, finished)
    movers = choose_movers(snapshots, priority)
    status = {"generated_at_utc": iso(finished), "started_at_utc": iso(started),
              "run_id": os.getenv("GITHUB_RUN_ID"), "cycle": os.getenv("RADAR_CYCLE", "1"), "event": os.getenv("GITHUB_EVENT_NAME", "local"),
              "duration_sec": round((finished - started).total_seconds(), 1),
              "market_feed": "Alpaca IEX; single venue, not consolidated SIP",
              "repository_private": private, "catalog_checked_on_ny": catalog["checked_on_ny"],
              "directory_complete": catalog.get("directory_complete", False),
              "fintual_evidence_current": catalog.get("fintual_evidence_current", False),
              "catalog_directory_fetched_at_utc": catalog.get("directory_fetched_at_utc"),
              "listed_candidates": sum(row["exchange"] not in {"NOT_IN_CURRENT_DIRECTORY", "UNKNOWN"} for row in assets.values()),
              "fintual_links_outside_directory": sum(row["exchange"] == "NOT_IN_CURRENT_DIRECTORY" for row in assets.values()),
              "fintual_links_verified": len(catalog["fintual_verified"]),
              "fintual_account_tradability_verified": False,
              "sector_filter_applied": False, "sector_classification_complete": False,
              "sector_proxies": [{"symbol": symbol, "sector": sector, "in_catalog": symbol in assets, "fintual_link_verified": symbol in catalog["fintual_verified"]} for symbol, sector in primary.SECTORS.items()],
              "sector_classification_source": primary.SECTOR_SOURCE,
              "sector_classification_scope": "11 sector ETF proxies only; individual equities remain unclassified",
              "primary_news_sources": news["sources"],
              "scanned_symbols": len(symbols), "symbols_with_snapshot": len(snapshots),
              "symbols_with_recent_iex_trade": sum(row["recent_trade_150sec"] for row in snapshots.values()),
              "symbols_with_change": sum(row["change_iex_pct"] is not None for row in snapshots.values()),
              "request_batches": (len(symbols) + CHUNK - 1) // CHUNK,
              "failed_batches": errors, "warnings": warnings,
              "price_history_enabled": private and bool(snapshots),
              "sec_primary_filings": filings,
              "coverage_note": "All listed equity/ETF candidates, across exchanges and sectors. Fintual links verify a subset, not user tradability.",
              "publication_note": "Public output has operational counts and SEC links only. Alpaca data redistribution is prohibited."}
    write_json(CATALOG, catalog)
    write_json(STATUS, status)
    audit = DOCS / "audit" / f"{date}.jsonl"
    audit.parent.mkdir(parents=True, exist_ok=True)
    with audit.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(status, ensure_ascii=False, separators=(",", ":")) + "\n")
    if private and snapshots:
        verified_set = set(catalog["fintual_verified"])
        selected = [{**row, "exchange": assets.get(row["symbol"], {}).get("exchange"),
                     "kind": assets.get(row["symbol"], {}).get("kind"),
                     "fintual_public_link_verified": row["symbol"] in verified_set,
                     "sector": primary.SECTORS.get(row["symbol"], "UNCLASSIFIED")} for row in movers["selected"]]
        report = {"generated_at_utc": iso(finished), "feed": status["market_feed"],
                  "catalog_size": len(symbols), "fintual_verified_count": len(catalog["fintual_verified"]),
                  "gainers": movers["gainers"], "losers": movers["losers"],
                  "unusual_iex_activity": movers["volume_activity"], "prices": selected,
                  "sec_primary_filings": filings, "batch_errors": errors,
                  "disclaimer": "IEX single venue. Activity uses prior IEX day and session fraction. Research only."}
        write_json(PRICES, report)
        history = ROOT / "history" / f"{date}.jsonl"
        history.parent.mkdir(exist_ok=True)
        with history.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(report, ensure_ascii=False, separators=(",", ":")) + "\n")
        rapid = f"# Radar Fintual · {iso(finished)}\n\nIEX: {len(snapshots)}/{len(symbols)} snapshots; {status['symbols_with_recent_iex_trade']} operaciones recientes.\n\nAlzas: {', '.join(movers['gainers'][:10]) or 'sin datos'}.\n\nBajas: {', '.join(movers['losers'][:10]) or 'sin datos'}.\n\nActividad IEX anormal aproximada: {', '.join(movers['volume_activity'][:10]) or 'sin datos'}.\n\nVer precios y timestamps individuales en docs/precios.json, y presentaciones primarias SEC enlazadas. No confirma comprabilidad en Fintual.\n"
    else:
        write_json(PRICES, {"status": "PUBLIC_NO_MARKET_DATA" if not private else "NO_NEW_QUOTES",
                            "generated_at_utc": iso(finished),
                            "reason": "Alpaca API data cannot be redistributed from a public repository." if not private else "No valid quotes; see docs/estado.json."})
        rapid = f"# Radar Fintual · {iso(finished)}\n\nCandidatos listados: {len(symbols)}; enlaces Fintual: {len(catalog['fintual_verified'])}; snapshots IEX: {len(snapshots)}.\n\nRepositorio público: auditoría y fuentes primarias SEC, sin cotizaciones Alpaca. Ver docs/estado.json.\n"
    (DOCS / "lectura_rapida.md").write_text(rapid, encoding="utf-8")
    print(json.dumps({"generated_at_utc": status["generated_at_utc"], "listed": len(symbols),
                      "fintual_links": len(catalog["fintual_verified"]), "snapshots": len(snapshots),
                      "recent": status["symbols_with_recent_iex_trade"],
                      "batch_failures": len(errors), "private_history": status["price_history_enabled"]}))
    return 0 if snapshots else 2


if __name__ == "__main__":
    sys.exit(run())
