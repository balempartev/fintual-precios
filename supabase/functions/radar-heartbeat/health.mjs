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
  const reason = !regularWindow ? 'OUTSIDE_REGULAR_WINDOW' :
    age === null ? 'NO_TIMESTAMP' : age < -60 ? 'FUTURE_TIMESTAMP' :
    age > 480 ? 'STALE_OR_MISSING' : state?.event !== 'schedule' ?
    'RECENT_MANUAL_NOT_SCHEDULED' : 'RECENT_SCHEDULED';
  return {
    observed_at_utc: instant.toISOString(),
    generated_at_utc: Number.isFinite(observed) ? new Date(observed).toISOString() : null,
    age_sec: age,
    status: reason,
    // A 404, closed market or missing feed is never labeled as successful coverage.
    market_clock_verified: false,
    run_id: state?.run_id == null ? null : String(state.run_id),
    event: state?.event == null ? null : String(state.event),
    snapshot_count: Number.isFinite(state?.symbols_with_snapshot) ? state.symbols_with_snapshot : null,
  };
}
