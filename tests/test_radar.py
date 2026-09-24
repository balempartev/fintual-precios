import datetime as dt
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import actualizar_precios as radar
import ejecutar_radar


class RadarTests(unittest.TestCase):
    def test_scheduled_collector_stops_on_closed_market(self):
        with patch.dict(os.environ, {'GITHUB_EVENT_NAME': 'schedule'}), \
             patch.object(ejecutar_radar, 'scheduled_market_open', return_value=False), \
             patch.object(ejecutar_radar, 'command') as command:
            self.assertEqual(ejecutar_radar.main(), 0)
        command.assert_not_called()
    def test_real_fintual_labels_are_multivalued_and_only_for_verified_symbols(self):
        page = ('<h3>Otra sección</h3><p>Falsa</p><h3>Etiquetas</h3>'
                '<div class="AssetTagChip_root__new"><p>🔬</p><p>Biotecnología</p></div>'
                '<div class="AssetTagChip_root__new"><div><p>📱</p></div><p>Tecnología</p></div>'
                '<h2>Otra sección</h2><div class="AssetTagChip_root__new"><p>❌</p><p>Incorrecta</p></div>')
        parser = radar.FintualTags()
        parser.feed(page)
        self.assertEqual(parser.tags, ['Biotecnología', 'Tecnología'])
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(radar, 'SECTOR_TAGS', Path(folder) / 'sectores.json'), \
                 patch.object(radar, 'get_bytes', return_value=page.encode()) as fetch, \
                 patch.object(radar.time, 'sleep'):
                result = radar.update_fintual_tags({'VKTX'}, ['FAKE', 'VKTX'], max_requests=3)
            self.assertEqual(result['with_public_tags'], 1)
            self.assertEqual(result['checked_this_cycle'], ['VKTX'])
            self.assertEqual(fetch.call_count, 1)
            self.assertIn('/vktx/', fetch.call_args.args[0])
    def test_fintual_404_is_recorded_but_not_mistaken_for_delisting(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(radar, 'SECTOR_TAGS', Path(folder) / 'sectores.json'), \
                 patch.object(radar, 'get_bytes', side_effect=RuntimeError('fintual.cl: HTTPError (404)')) as fetch, \
                 patch.object(radar.time, 'sleep'):
                first = radar.update_fintual_tags({'ABNB'}, ['ABNB'], max_requests=1)
                second = radar.update_fintual_tags({'ABNB'}, ['ABNB'], max_requests=1)
            self.assertEqual(first['http_404_unverified'], 1)
            self.assertEqual(first['with_public_tags'], 0)
            self.assertEqual(second['checked_this_cycle'], [])
            self.assertEqual(fetch.call_count, 1)
    def test_http_failure_is_safe_and_does_not_expose_url_credentials(self):
        from urllib.error import HTTPError
        with patch.object(radar, "urlopen", side_effect=HTTPError("https://example.test", 403, "Forbidden", {}, None)):
            with self.assertRaisesRegex(RuntimeError, r"HTTPError \(403\)"):
                radar.get_bytes("https://example.test?token=private")


    def test_listed_stocks_and_etfs_with_public_fintual_links(self):
        nasdaq = (b"Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares\n"
                  b"AAPL|Apple Inc - Common Stock|Q|N|N|100|N|N\n"
                  b"VOO|Vanguard S&P ETF|G|N|N|100|Y|N\n"
                  b"TEST|Fake|G|Y|N|100|N|N\n"
                  b"FOOW|Foo - Warrants|G|N|N|100|N|N\n")
        other = (b"ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol\n"
                 b"GE|General Electric - Common Stock|N|GE|N|100|N|GE\n")
        a = radar.parse_directory(nasdaq, "nasdaqlisted.txt")
        b = radar.parse_directory(other, "otherlisted.txt")
        self.assertEqual(set(a), {"AAPL", "VOO"})
        self.assertEqual(b["GE"]["exchange"], "NYSE")
        parser = radar.FintualLinks()
        parser.feed('<a href="https://fintual.cl/f/acciones/aapl/">Apple</a><a href="/f/acciones/voo/">ETF</a>')
        self.assertEqual(parser.symbols, {"AAPL", "VOO"})

    def test_failed_catalog_does_not_claim_historical_symbols_as_verified(self):
        with patch.object(radar, "get_bytes", side_effect=RuntimeError("unavailable")), \
             patch.object(radar, "historical_symbols", return_value={"OLD"}):
            catalog = radar.refresh_catalog(None, "2026-09-23")
        self.assertFalse(catalog["directory_complete"])
        self.assertFalse(catalog["fintual_evidence_current"])
        self.assertEqual(catalog["fintual_verified"], [])
        self.assertIsNone(catalog["directory_fetched_at_utc"])

    def test_fintual_symbols_outside_directory_are_retained_with_distinct_evidence(self):
        listed = {f"L{i}": {"symbol": f"L{i}", "exchange": "NASDAQ", "kind": "EQUITY_CANDIDATE"} for i in range(7000)}
        html = "".join(f'<a href="https://fintual.cl/f/acciones/f{i}/">Stock</a>' for i in range(1500)).encode()
        with patch.object(radar, "get_bytes", side_effect=[b"a", b"b", html]), \
             patch.object(radar, "parse_directory", side_effect=[dict(list(listed.items())[:5000]), dict(list(listed.items())[5000:])]):
            catalog = radar.refresh_catalog(None, "2026-09-23")
        self.assertTrue(catalog["directory_complete"])
        self.assertTrue(catalog["fintual_evidence_current"])
        self.assertEqual(len(catalog["assets"]), 8500)
        self.assertEqual(len(catalog["fintual_verified"]), 1500)
        asset = next(row for row in catalog["assets"] if row["symbol"] == "F0")
        self.assertEqual(asset["kind"], "FINTUAL_LINK_ONLY")

    def test_individual_time_freshness_and_opposite_movers(self):
        finished = dt.datetime(2026, 9, 23, 15, 20, 0, tzinfo=dt.timezone.utc)
        base = {"latestQuote": {"t": "2026-09-23T15:19:55Z", "bp": 10, "ap": 10.1},
                "dailyBar": {"v": 3000}, "prevDailyBar": {"c": 10, "v": 2000}}
        rising = radar.parse_snapshot("RISE", {**base, "latestTrade": {"p": 11, "t": "2026-09-23T15:19:59Z"}}, finished)
        falling = radar.parse_snapshot("FALL", {**base, "latestTrade": {"p": 9, "t": "2026-09-23T15:19:58Z"}}, finished)
        future = radar.parse_snapshot("FUTURE", {**base, "latestTrade": {"p": 100, "t": "2026-09-23T15:20:05Z"}}, finished)
        stale = radar.parse_snapshot("STALE", {**base, "latestTrade": {"p": 100, "t": "2026-09-22T15:19:59Z"}}, finished)
        self.assertEqual((rising["change_iex_pct"], falling["change_iex_pct"]), (10.0, -10.0))
        self.assertIsNone(future["change_iex_pct"])
        self.assertIsNone(stale["change_iex_pct"])
        movers = radar.choose_movers({r["symbol"]: r for r in [rising, falling, future, stale]}, ["FUTURE"])
        self.assertEqual(movers["gainers"], ["RISE"])
        self.assertEqual(movers["losers"], ["FALL"])
        self.assertIn("FUTURE", [r["symbol"] for r in movers["selected"]])
        later = finished + dt.timedelta(minutes=4)
        radar.finalize_freshness({"RISE": rising}, later)
        self.assertIsNone(rising["change_iex_pct"])
        self.assertFalse(rising["recent_quote_60sec"])

    def test_public_has_no_market_data_private_preserves_consultable_history(self):
        instant = dt.datetime(2026, 9, 23, 15, 20, 0, tzinfo=dt.timezone.utc)
        quote = radar.parse_snapshot("AAPL", {
            "latestTrade": {"p": 11, "t": "2026-09-23T15:19:59Z"},
            "latestQuote": {"bp": 10.9, "ap": 11.1, "t": "2026-09-23T15:19:59Z"},
            "dailyBar": {"v": 1000}, "prevDailyBar": {"c": 10, "v": 2000},
        }, instant)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "prioridad.txt").write_text("AAPL\n")
            catalog = {"checked_on_ny": "2026-09-23", "directory_fetched_at_utc": radar.iso(instant),
                       "assets": [{"symbol": "AAPL", "exchange": "NASDAQ", "kind": "EQUITY_CANDIDATE"}],
                       "fintual_verified": ["AAPL"], "warnings": [], "sources": {}}
            with patch.multiple(radar, ROOT=root, DOCS=root / "docs",
                                CATALOG=root / "docs/catalogo.json",
                                STATUS=root / "docs/estado.json",
                                PRICES=root / "docs/precios.json",
                                SECTOR_TAGS=root / "docs/sectores.json"), \
                 patch.object(radar, "now_utc", return_value=instant), \
                 patch.object(radar, "get_bytes", return_value=b'<h3>Etiquetas</h3><div class="AssetTagChip_root"><p>X</p><p>Tecnologia</p></div>'), \
                 patch.object(radar, "refresh_catalog", return_value=catalog), \
                 patch.object(radar, "fetch_snapshots", return_value=({"AAPL": quote}, [])), \
                 patch.object(radar, "sec_filings", return_value=([], [])), \
                 patch.object(radar.primary, "collect", return_value={"items": [], "sources": []}), \
                 patch.dict(os.environ, {"ALPACA_API_KEY_ID": "synthetic", "ALPACA_API_SECRET_KEY": "synthetic",
                                        "GITHUB_REPOSITORY_PRIVATE": "false"}):
                self.assertEqual(radar.run(), 0)
                public = (root / "docs/precios.json").read_text()
                self.assertNotIn('"price_iex_usd"', public)
                self.assertNotIn('"11"', public)
                self.assertFalse((root / "history").exists())
                os.environ["GITHUB_REPOSITORY_PRIVATE"] = "true"
                self.assertEqual(radar.run(), 0)
                self.assertEqual(radar.run(), 0)
                private = json.loads((root / "docs/precios.json").read_text())
                self.assertEqual(private["prices"][0]["price_iex_usd"], 11)
                lines = (root / "history/2026-09-23.jsonl").read_text().splitlines()
                self.assertEqual(len(lines), 2)
                self.assertEqual(json.loads(lines[1])["prices"][0]["trade_utc"], "2026-09-23T15:19:59Z")


if __name__ == "__main__":
    unittest.main()
