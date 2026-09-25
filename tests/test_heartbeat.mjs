import { test } from 'node:test';
import { strict as assert } from 'node:assert';
import { inspectRadar } from '../supabase/functions/radar-heartbeat/health.mjs';

test('recent manual data never proves scheduled freshness', () => {
  const now = new Date('2026-09-25T13:35:00Z');
  const report = inspectRadar({ generated_at_utc: '2026-09-25T13:34:00Z',
    run_id: 123, event: 'workflow_dispatch', symbols_with_snapshot: 11872 }, now);
  assert.equal(report.status, 'RECENT_MANUAL_NOT_SCHEDULED');
  assert.equal(report.age_sec, 60);
  assert.equal(report.market_clock_verified, false);
});

test('scheduled data older than eight minutes is stale', () => {
  const r = inspectRadar({ generated_at_utc: '2026-09-25T13:31:00Z', event: 'schedule' },
    new Date('2026-09-25T13:40:00Z'));
  assert.equal(r.status, 'STALE_OR_MISSING');
});

test('New York time and weekends gate the signal', () => {
  assert.equal(inspectRadar(null, new Date('2026-09-25T13:29:00Z')).status, 'OUTSIDE_REGULAR_WINDOW');
  assert.equal(inspectRadar(null, new Date('2026-09-25T13:30:00Z')).status, 'NO_TIMESTAMP');
  assert.equal(inspectRadar(null, new Date('2026-09-26T13:30:00Z')).status, 'OUTSIDE_REGULAR_WINDOW');
  assert.equal(inspectRadar({ generated_at_utc: '2026-11-02T14:31:00Z', event: 'schedule',
    scanned_symbols: 100, symbols_with_snapshot: 90,
    symbols_with_recent_iex_trade: 3, failed_batches: [] },
    new Date('2026-11-02T14:33:00Z')).status, 'RECENT_SCHEDULED');
});

test('a timely schedule with zero data or failed batches is incomplete', () => {
  const now = new Date('2026-09-25T13:35:00Z');
  const base = { generated_at_utc: '2026-09-25T13:34:00Z', event: 'schedule',
    scanned_symbols: 100, symbols_with_snapshot: 90,
    symbols_with_recent_iex_trade: 4, failed_batches: [] };
  assert.equal(inspectRadar({ ...base, symbols_with_snapshot: 0 }, now).status,
    'INCOMPLETE_CAPTURE');
  assert.equal(inspectRadar({ ...base, failed_batches: [{ batch_start: 'A' }] }, now).status,
    'INCOMPLETE_CAPTURE');
  assert.equal(inspectRadar(base, now).status, 'RECENT_SCHEDULED');
});
