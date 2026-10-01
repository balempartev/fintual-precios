import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import actualizar_precios as radar

class ClosureTests(unittest.TestCase):
    def test_intersection_counters_exclude_market_only_and_link_only(self):
        cat={'fintual_verified':['A','B','C'], 'assets':{'A':{'exchange':'NASDAQ'},'B':{'exchange':'NYSE'},'C':{'exchange':'NOT_IN_CURRENT_DIRECTORY'},'D':{'exchange':'NASDAQ'}}}
        r=radar.fintual_screen_metrics(cat,['A','B','C','D'],{'A':{'recent_trade_150sec':True},'D':{'recent_trade_150sec':True}},[{'symbols':['B'],'error':'outage'}])
        self.assertEqual((r['public_total'],r['market_intersection'],r['sent'],r['processed'],r['with_data'],r['without_data'],r['errors'],r['coverage_pct']),(3,2,2,2,1,1,1,50))
        self.assertFalse(r['licensed_individual_results_public'])

    def test_untouched_page_precedes_old_404_retry(self):
        with TemporaryDirectory() as d, patch.object(radar,'SECTOR_TAGS',Path(d)/'sectors.json'), patch.object(radar,'get_bytes',side_effect=RuntimeError('fintual.cl: HTTPError (404)')), patch.object(radar.time,'sleep'):
            radar.write_json(radar.SECTOR_TAGS,{'symbols':{'A':{'status':'HTTP_404','checked_at_utc':'2026-01-01T00:00:00Z','tags':[]}}})
            r=radar.update_fintual_tags({'A','B'},['A'],max_requests=1)
            self.assertEqual(r['checked_this_cycle'],['B'])
            self.assertEqual(r['unclassified'],2)
            self.assertEqual(r['symbols']['B']['cause'],'UNRESOLVED_NOT_PROOF_OF_REMOVAL')

    def test_no_public_tags_are_not_cached_forever(self):
        with TemporaryDirectory() as d, patch.object(radar,'SECTOR_TAGS',Path(d)/'sectors.json'), patch.object(radar,'get_bytes',return_value=b'<h3>Etiquetas</h3>') as fetch, patch.object(radar.time,'sleep'):
            radar.write_json(radar.SECTOR_TAGS,{'symbols':{'A':{'status':'NO_PUBLIC_TAGS','checked_at_utc':'2026-01-01T00:00:00Z','tags':[]}}})
            r=radar.update_fintual_tags({'A'},[],max_requests=1)
            self.assertEqual(fetch.call_count,1)
            self.assertEqual(r['coverage_pct'],0)

if __name__=='__main__':unittest.main()
