import datetime as dt
import unittest
from vigilancia import evaluate
from fuentes_primarias import parse_feed
UTC=dt.timezone.utc
class AcceptanceTests(unittest.TestCase):
 def rows(self):
  return [{'run_id':str(n),'event':'schedule','started_at_utc':f'2026-09-24T13:{m}:00Z','generated_at_utc':f'2026-09-24T13:{m+1}:00Z','scanned_symbols':100,'symbols_with_snapshot':90,'symbols_with_recent_iex_trade':12,'failed_batches':[]} for n,m in enumerate([32,37,42])]
 def test_three_distinct_schedule_events_pass(self):
  r=evaluate(self.rows(),dt.datetime(2026,9,24,13,55,tzinfo=UTC),True)
  self.assertEqual(r['opening_acceptance'],'PASSED')
 def test_manual_cycles_and_repeated_run_never_count_as_scheduler_proof(self):
  for mode in ['workflow_dispatch','same_run']:
   rows=self.rows()
   for r in rows:
    if mode=='same_run':r['run_id']='same'
    else:r['event']=mode
   self.assertEqual(evaluate(rows,dt.datetime(2026,9,24,13,55,tzinfo=UTC),True)['opening_acceptance'],'FAILED')
 def test_stale_capture_detected_independent_of_collector(self):
  self.assertEqual(evaluate(self.rows(),dt.datetime(2026,9,24,15,tzinfo=UTC),True)['health'],'STALE_OR_MISSING')
  self.assertEqual(evaluate([],dt.datetime(2026,9,24,22,tzinfo=UTC),False)['health'],'CLOSED')
 def test_freshness_and_coverage_required(self):
  for key,value in [('symbols_with_recent_iex_trade',0),('symbols_with_snapshot',10),('failed_batches',[{'error':'timeout'}])]:
   rows=self.rows()
   for row in rows:row[key]=value
   self.assertEqual(evaluate(rows,dt.datetime(2026,9,24,13,55,tzinfo=UTC),True)['opening_acceptance'],'FAILED')
 def test_feed_future_rejected_missing_time_explicit(self):
  data=b'<rss><channel><item><title>Future</title><link>https://www.fda.gov/future</link><pubDate>Fri, 25 Sep 2026 12:00:00 GMT</pubDate></item><item><title>Unknown date</title><link>https://www.fda.gov/item</link></item></channel></rss>'
  r=parse_feed(data,'FDA',dt.datetime(2026,9,24,13,tzinfo=UTC));self.assertEqual(len(r),1);self.assertIsNone(r[0]['published_at_utc']);self.assertFalse(r[0]['price_causality_verified'])
