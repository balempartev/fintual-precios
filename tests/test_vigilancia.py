import datetime as dt
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import vigilancia
from vigilancia import evaluate
from fuentes_primarias import parse_feed
UTC=dt.timezone.utc
class AcceptanceTests(unittest.TestCase):
 def test_form_reminders_chile_time_and_idempotent_issue(self):
  # September Chile is UTC-3; January is also UTC-3, with Sunday independent of NY session.
  cases=[(dt.datetime(2026,9,24,13,6,tzinfo=UTC),('2026-09-24','10:00')),
         (dt.datetime(2026,9,24,20,16,tzinfo=UTC),('2026-09-24','17:00')),
         (dt.datetime(2026,9,27,21,6,tzinfo=UTC),('2026-09-27','18:00')),
         (dt.datetime(2026,9,27,21,26,tzinfo=UTC),None),
         (dt.datetime(2026,9,26,13,6,tzinfo=UTC),None)]
  for now,expected in cases:self.assertEqual(vigilancia.form_slot(now),expected)
  with patch.object(vigilancia,'api',return_value=[{'title':'slot','number':4,'html_url':'https://github.com/example/issues/4'}]) as api:
   self.assertTrue(vigilancia.issue('slot','safe text')['existing'])
   self.assertEqual(api.call_count,1)
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
 def test_dispatch_error_still_persists_incident(self):
  now=dt.datetime.now(UTC);date=now.astimezone(vigilancia.NY).date().isoformat()
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);audit=root/'docs'/'audit';audit.mkdir(parents=True)
   (audit/(date+'.jsonl')).write_text(json.dumps({'run_id':'old','generated_at_utc':(now-dt.timedelta(minutes=12)).isoformat(),'symbols_with_snapshot':10})+'\n')
   with patch.object(vigilancia,'ROOT',root),patch.object(vigilancia,'urlopen',return_value=io.BytesIO(b'{"is_open":true}')),patch.object(vigilancia,'api',side_effect=RuntimeError('GitHub API status 503')),patch.object(vigilancia,'issue',return_value={'number':7,'url':'https://github.com/example/issues/7'}),patch.dict(os.environ,{'GITHUB_REPOSITORY':'owner/repo','GITHUB_RUN_ID':'test','ALPACA_API_KEY_ID':'synthetic','ALPACA_API_SECRET_KEY':'synthetic'}):
    self.assertEqual(vigilancia.main(),1)
   report=json.loads((root/'docs'/'vigilancia.json').read_text())
   self.assertEqual(report['health'],'STALE_OR_MISSING')
   self.assertEqual(report['recovery_error'],'GitHub API status 503')
   self.assertEqual(report['incident']['number'],7)
   self.assertEqual(json.loads((root/'docs'/'recovery_state.json').read_text())['attempts'],0)
 def test_recovered_capture_comments_once_without_claiming_cron(self):
  now=dt.datetime.now(UTC);date=now.astimezone(vigilancia.NY).date().isoformat()
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);audit=root/'docs'/'audit';audit.mkdir(parents=True)
   (audit/(date+'.jsonl')).write_text(json.dumps({'run_id':'new','generated_at_utc':(now-dt.timedelta(seconds=30)).isoformat(),'symbols_with_snapshot':10})+'\n')
   (root/'docs'/'vigilancia.json').write_text(json.dumps({'date_ny':date,'incident':{'number':7}}))
   (root/'docs'/'recovery_state.json').write_text(json.dumps({'date':date,'attempts':1,'last_attempt':None}))
   with patch.object(vigilancia,'ROOT',root),patch.object(vigilancia,'urlopen',return_value=io.BytesIO(b'{"is_open":true}')),patch.object(vigilancia,'api',return_value={}) as api,patch.object(vigilancia,'issue',return_value={'number':7,'url':'https://github.com/example/issues/7'}),patch.dict(os.environ,{'GITHUB_REPOSITORY':'owner/repo','GITHUB_RUN_ID':'test','ALPACA_API_KEY_ID':'synthetic','ALPACA_API_SECRET_KEY':'synthetic'}):
    vigilance_result=vigilancia.main()
   report=json.loads((root/'docs'/'vigilancia.json').read_text())
   self.assertIn(vigilance_result,(0,1))
   self.assertEqual(report['recovery'],'CAPTURE_RESTORED_NOTIFIED')
   self.assertEqual(api.call_count,1)
   self.assertIn('/issues/7/comments',api.call_args.args[0])
   self.assertTrue(json.loads((root/'docs'/'recovery_state.json').read_text())['recovery_notified'])
