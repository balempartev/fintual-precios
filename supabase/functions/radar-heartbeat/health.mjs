/** Operational evidence only. Never derives or publishes licensed market quotes. */
const NY = new Intl.DateTimeFormat('en-US', {
  timeZone: 'America/New_York', weekday: 'short', hour: '2-digit', minute: '2-digit',
  hourCycle: 'h23',
});

export function inspectRadar(state, instant = new Date()) {
  const parts = Object.fromEntries(NY.formatToParts(instant).map(({ type, value }) => [type, value]));
  const minute = Number(parts.hour) * 60 + Number(parts.minute);
  const regularWindow = !['Sat', 'Sun'].includes(parts.weekday) && minute >= 570 && minute < 960;
  // The wall-clock window alone cannot establish holidays or early closes.
  const observed = state?.generated_at_utc ? Date.parse(state.generated_at_utc) : NaN;
  const age = Number.isFinite(observed) ? Math.round((instant.getTime() - observed) / 1000) : null;
  const count = state?.symbols_with_snapshot;
  const scanned = state?.scanned_symbols;
  const complete = Number.isInteger(count) && Number.isInteger(scanned) && scanned > 0 &&
    count / scanned >= 0.8 && Number.isInteger(state?.symbols_with_recent_iex_trade) &&
    state.symbols_with_recent_iex_trade > 0 && Array.isArray(state?.failed_batches) &&
    state.failed_batches.length === 0;
  const reason = !regularWindow ? 'OUTSIDE_REGULAR_WINDOW' :
    age === null ? 'NO_TIMESTAMP' : age < -60 ? 'FUTURE_TIMESTAMP' :
    age > 480 ? 'STALE_OR_MISSING' : state?.event !== 'schedule' ?
    'RECENT_MANUAL_NOT_SCHEDULED' : complete ? 'RECENT_SCHEDULED' : 'INCOMPLETE_CAPTURE';
  return {
    observed_at_utc: instant.toISOString(),
    generated_at_utc: Number.isFinite(observed) ? new Date(observed).toISOString() : null,
    age_sec: age,
    status: reason,
    // A 404, closed market or missing feed is never labeled as successful coverage.
    market_clock_verified: false,
    run_id: state?.run_id == null ? null : String(state.run_id),
    event: state?.event == null ? null : String(state.event),
    snapshot_count: Number.isFinite(count) ? count : null,
  };
}
