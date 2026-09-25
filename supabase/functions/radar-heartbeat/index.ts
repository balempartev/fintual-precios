/** Optional independent scheduler probe. No Alpaca keys or private portfolio data. */
import { inspectRadar } from './health.mjs';

const source = 'https://raw.githubusercontent.com/balempartev/fintual-precios/main/docs/estado.json';
const jsonHeaders = { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' };

Deno.serve(async (request) => {
  if (request.method !== 'POST') return new Response('POST required', { status: 405 });
  const secret = Deno.env.get('RADAR_HEARTBEAT_TOKEN');
  if (!secret || request.headers.get('authorization') !== `Bearer ${secret}`) {
    return new Response('Unauthorized', { status: 401 });
  }
  const url = Deno.env.get('SUPABASE_URL');
  const key = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
  if (!url || !key) return new Response('Service configuration missing', { status: 503 });
  let record;
  try {
    const response = await fetch(source, { headers: { accept: 'application/json' }, cache: 'no-store',
      signal: AbortSignal.timeout(8000) });
    if (!response.ok) throw new Error(`SOURCE_HTTP_${response.status}`);
    record = inspectRadar(await response.json());
  } catch (error) {
    record = { ...inspectRadar(null), status: 'SOURCE_UNAVAILABLE',
      source_error: error instanceof Error ? error.message.slice(0, 80) : 'UNKNOWN' };
  }
  const payload = {
    observed_at_utc: record.observed_at_utc,
    generated_at_utc: record.generated_at_utc,
    status: record.status,
    age_sec: record.age_sec,
    run_id: record.run_id,
    event: record.event,
    snapshot_count: record.snapshot_count,
    source_error: record.source_error ?? null,
  };
  const stored = await fetch(`${url}/rest/v1/radar_heartbeat`, {
    method: 'POST', headers: { ...jsonHeaders, apikey: key, authorization: `Bearer ${key}`,
      prefer: 'return=minimal' }, body: JSON.stringify(payload), signal: AbortSignal.timeout(8000),
  });
  if (!stored.ok) return new Response(JSON.stringify({ status: 'STORE_FAILED', code: stored.status }),
    { status: 503, headers: jsonHeaders });
  return new Response(JSON.stringify({ status: record.status, observed_at_utc: record.observed_at_utc }),
    { headers: jsonHeaders });
});
