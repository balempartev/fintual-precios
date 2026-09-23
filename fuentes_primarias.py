"""Government primary feeds. Store links and metadata, no inferred price causality."""
import datetime as dt
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
FEEDS={
 'Federal Reserve':'https://www.federalreserve.gov/feeds/press_all.xml',
 'FDA press':'https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml',
 'FDA drugs':'https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/drugs/rss.xml',
}
SECTORS={'XLC':'Comunicación','XLY':'Consumo discrecional','XLP':'Consumo básico','XLE':'Energía','XLF':'Finanzas','XLV':'Salud','XLI':'Industria','XLB':'Materiales','XLRE':'Inmobiliario','XLK':'Tecnología','XLU':'Servicios públicos'}
SECTOR_SOURCE='https://www.ssga.com/us/en/intermediary/capabilities/equities/sector-investing/select-sector-etfs'

def parse_feed(body,source,now):
 root=ET.fromstring(body);out=[]
 for item in root.findall('.//item')[:30]:
  url=item.findtext('link','').strip();title=item.findtext('title','').strip();raw=item.findtext('pubDate','').strip()
  if not url.startswith(('https://','http://')) or not title:continue
  try:
   when=parsedate_to_datetime(raw)
   when=when.astimezone(dt.timezone.utc) if when.tzinfo else None
  except (ValueError,TypeError):when=None
  if when and when>now+dt.timedelta(minutes=1):continue
  out.append({'source':source,'title':title[:300],'url':url,'published_at_utc':when.isoformat() if when else None,'retrieved_at_utc':now.isoformat(),'price_causality_verified':False})
 return out

def collect(get_bytes,now):
 def one(pair):
  name,url=pair
  try:
   items=parse_feed(get_bytes(url,attempts=2,timeout=8),name,now)
   return items,{'source':name,'url':url,'status':'OK' if items else 'EMPTY','items':len(items)}
  except Exception as e:return [],{'source':name,'url':url,'status':'FAILED','error':str(e) if isinstance(e,RuntimeError) else type(e).__name__}
 all_items=[];statuses=[]
 with ThreadPoolExecutor(max_workers=3) as pool:
  for items,status in pool.map(one,FEEDS.items()):all_items+=items;statuses.append(status)
 return {'generated_at_utc':now.isoformat(),'items':all_items,'sources':statuses,'scope':'FDA + Federal Reserve. SEC filings handled separately. Not exhaustive corporate IR/news coverage.'}
