"""Independent job: operational ledger, bounded recovery and acceptance evidence.
No private account data and no Alpaca per-symbol data enter public files.
"""
import datetime as dt
import json
import os
from pathlib import Path
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parent
NY=ZoneInfo('America/New_York')
CL=ZoneInfo('America/Santiago')
UTC=dt.timezone.utc

def form_slot(now):
    """A narrow local-time window; reruns are deduplicated by issue title."""
    local=now.astimezone(CL)
    if local.minute>=25:return None
    hour=local.hour
    if (local.weekday()<5 and hour in (10,17)) or (local.weekday()==6 and hour==18):
        return local.date().isoformat(),f'{hour:02d}:00'
    return None

def parsed(s):
    try:
        t=dt.datetime.fromisoformat(s.replace('Z','+00:00'))
        return t.astimezone(UTC) if t.tzinfo else None
    except (ValueError,TypeError,AttributeError):return None

def evaluate(records,now,market_open):
    local=now.astimezone(NY)
    valid=[r for r in records if parsed(r.get('generated_at_utc')) and parsed(r['generated_at_utc']).astimezone(NY).date()==local.date()]
    latest=max(valid,key=lambda r:r['generated_at_utc']) if valid else None
    age=(now-parsed(latest['generated_at_utc'])).total_seconds() if latest else None
    health='CLOSED' if not market_open else 'HEALTHY' if latest and 0<=age<=480 and latest.get('symbols_with_snapshot',0)>0 else 'STALE_OR_MISSING'
    window=[]
    for r in valid:
        t=parsed(r['generated_at_utc']).astimezone(NY)
        start=parsed(r.get('started_at_utc'))
        st=start.astimezone(NY) if start else t
        if r.get('event')=='schedule' and r.get('run_id') and st.hour==9 and 30<=st.minute<=50 and t.hour==9 and t.minute<=55:
            if r.get('symbols_with_recent_iex_trade',0)>0 and r.get('symbols_with_snapshot',0)>=.8*max(1,r.get('scanned_symbols',0)) and not r.get('failed_batches'):
                if r['run_id'] not in {x['run_id'] for x in window}:window.append(r)
    window.sort(key=lambda r:r['started_at_utc'])
    gaps=[(parsed(b['started_at_utc'])-parsed(a['started_at_utc'])).total_seconds() for a,b in zip(window,window[1:])]
    passed=any(180<=gaps[i]<=420 and 180<=gaps[i+1]<=420 for i in range(max(0,len(gaps)-1)))
    due=(local.hour,local.minute)>=(9,55)
    return {'health':health,'age_sec':age,'latest_run_id':latest.get('run_id') if latest else None,
            'opening_acceptance':'PASSED' if passed else 'FAILED' if due and market_open else 'PENDING',
            'genuine_schedule_runs':[r['run_id'] for r in window], 'start_gaps_sec':gaps,
            'criteria':'3 distinct schedule events starting NY09:30–09:50, gaps 180–420s, >=80% snapshots, fresh trades >0, no failed batches',
            'task_publication_monitor':'BLOCKED_NO_EXTERNAL_TASKS_RECEIPT_API',
            'work_credits_required':False,'same_provider_limitation':'This watchdog is independent of the collector job, but shares GitHub availability.'}

def api(path,method='GET',body=None):
    repo=os.environ['GITHUB_REPOSITORY'];token=os.environ['GH_TOKEN']
    req=Request('https://api.github.com/repos/'+repo+path,method=method,data=None if body is None else json.dumps(body).encode(),headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','User-Agent':'RadarFintual-watchdog'})
    try:
        with urlopen(req,timeout=15) as r:return json.load(r) if r.status!=204 else {}
    except HTTPError as e:raise RuntimeError('GitHub API status '+str(e.code)) from None

def issue(title,body):
    current=api('/issues?state=open&per_page=100')
    old=next((i for i in current if i.get('title')==title),None)
    if old:return {'number':old['number'],'url':old['html_url'],'existing':True}
    result=api('/issues','POST',{'title':title,'body':body,'assignees':[os.environ['GITHUB_REPOSITORY'].split('/')[0]]})
    return {'number':result['number'],'url':result['html_url'],'existing':False}

def main():
    now=dt.datetime.now(UTC);date=now.astimezone(NY).date().isoformat();path=ROOT/'docs'/'audit'/f'{date}.jsonl'
    records=[]
    for line in path.read_text().splitlines() if path.exists() else []:
        try:records.append(json.loads(line))
        except ValueError:pass
    clock_error=None
    try:
        headers={'APCA-API-KEY-ID':os.environ['ALPACA_API_KEY_ID'],'APCA-API-SECRET-KEY':os.environ['ALPACA_API_SECRET_KEY']}
        with urlopen(Request('https://paper-api.alpaca.markets/v2/clock',headers=headers),timeout=12) as r:clock=json.load(r)
        market_open=clock.get('is_open') is True
    except Exception as e:market_open=False;clock_error=type(e).__name__
    report=evaluate(records,now,market_open)
    if clock_error:report['health']='UNKNOWN_CLOCK';report['clock_error']=clock_error
    previous_path=ROOT/'docs'/'vigilancia.json'
    try:previous=json.loads(previous_path.read_text())
    except (OSError,ValueError):previous={}
    if report['opening_acceptance']=='PENDING' and previous.get('date_ny')==date and previous.get('opening_acceptance') in {'PASSED','FAILED'}:
        for field in ['opening_acceptance','genuine_schedule_runs','start_gaps_sec']:report[field]=previous[field]
    report.update({'checked_at_utc':now.isoformat(),'date_ny':date,'watchdog_run_id':os.environ.get('GITHUB_RUN_ID'),'recovery':None,'notification_receipt':'UNVERIFIED'})
    statepath=ROOT/'docs'/'recovery_state.json'
    try:state=json.loads(statepath.read_text())
    except (OSError,ValueError):state={}
    if state.get('date')!=date:state={'date':date,'attempts':0,'last_attempt':None}
    if not state.get('incident_number') and previous.get('date_ny')==date:
        state['incident_number']=(previous.get('incident') or {}).get('number')
    last=parsed(state.get('last_attempt'));cooldown=not last or (now-last).total_seconds()>=600
    if report['health']=='STALE_OR_MISSING' and state['attempts']<2 and cooldown:
        try:
            api('/actions/workflows/precios.yml/dispatches','POST',{'ref':'main','inputs':{'validation_cycles':'1'}})
            state['attempts']+=1;state['last_attempt']=now.isoformat();report['recovery']='DISPATCH_REQUESTED_NOT_COMPLETED'
        except RuntimeError as e:report['recovery_error']=str(e)
    if os.getenv('NOTIFICATION_TEST')=='true':
        try:
            report['notification_test_issue']=issue('Radar Fintual · prueba técnica de avisos '+date,'Prueba inocua solicitada por el propietario. No contiene precios, posiciones ni claves. Recibir esta incidencia confirma únicamente el canal de GitHub; no prueba push/email de ChatGPT Tasks.\n\nEjecución: https://github.com/'+os.environ['GITHUB_REPOSITORY']+'/actions/runs/'+os.environ['GITHUB_RUN_ID'])
        except RuntimeError as e:report['notification_test_error']=str(e)
    slot=form_slot(now)
    if slot:
        title='Radar Fintual · confirmar cartera '+slot[0]+' '+slot[1]+' Chile'
        try:
            report['form_reminder']=issue(title,'Recordatorio de confirmación en el formulario privado de Radar Fintual. Este aviso técnico procede de GitHub; no acredita push ni ejecución de ChatGPT Tasks. No publiques aquí posiciones, saldos ni órdenes.')
        except RuntimeError as e:report['form_reminder_error']=str(e)
    if report['health'] in {'STALE_OR_MISSING','UNKNOWN_CLOCK'} or report['opening_acceptance']=='FAILED':
        try:
            report['incident']=issue('Radar Fintual · incidencia de captura '+date,'Estado técnico: '+report['health']+'; prueba de apertura: '+report['opening_acceptance']+'. Revisa docs/vigilancia.json. Recuperación limitada a 2 intentos diarios con separación de 10 min. No implica que un informe financiero haya sido publicado.')
            state['incident_number']=report['incident']['number']
        except RuntimeError as e:report['incident_error']=str(e)
    if report['health']=='HEALTHY' and state.get('incident_number') and not state.get('recovery_notified'):
        try:
            api('/issues/'+str(state['incident_number'])+'/comments','POST',{'body':'Captura recuperada: nueva ejecución '+str(report['latest_run_id'])+'; edad '+str(round(report['age_sec']))+' s a '+now.isoformat()+'. La puntualidad del cron y la entrega de informes ChatGPT requieren pruebas independientes.'})
            state['recovery_notified']=True
            report['recovery']='CAPTURE_RESTORED_NOTIFIED'
        except RuntimeError as e:report['recovery_notification_error']=str(e)
    bad=report['health'] in {'STALE_OR_MISSING','UNKNOWN_CLOCK'} or report['opening_acceptance']=='FAILED'
    previous_bad=previous.get('date_ny')==date and (previous.get('health') in {'STALE_OR_MISSING','UNKNOWN_CLOCK'} or previous.get('opening_acceptance')=='FAILED')
    signal_failure=bad and not state.get('failure_signaled') and not previous_bad
    if bad:state['failure_signaled']=True
    report['failure_email_once_per_day']=signal_failure
    statepath.write_text(json.dumps(state,indent=2)+'\n')
    (ROOT/'docs'/'vigilancia.json').write_text(json.dumps(report,indent=2)+'\n')
    hist=ROOT/'docs'/'vigilancia';hist.mkdir(exist_ok=True)
    with (hist/(date+'.jsonl')).open('a') as f:f.write(json.dumps(report)+'\n')
    print(json.dumps(report))
    return 1 if signal_failure else 0
if __name__=='__main__':sys.exit(main())
