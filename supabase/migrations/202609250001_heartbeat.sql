-- Staging only; do not schedule or expose this table before a free project is connected.
create table if not exists public.radar_heartbeat (
  id bigint generated always as identity primary key,
  observed_at_utc timestamptz not null,
  generated_at_utc timestamptz,
  status text not null check (status in (
    'OUTSIDE_REGULAR_WINDOW', 'NO_TIMESTAMP', 'FUTURE_TIMESTAMP',
    'STALE_OR_MISSING', 'RECENT_MANUAL_NOT_SCHEDULED', 'RECENT_SCHEDULED',
    'INCOMPLETE_CAPTURE',
    'SOURCE_UNAVAILABLE')),
  age_sec integer,
  run_id text,
  event text,
  snapshot_count integer,
  source_error text,
  inserted_at timestamptz not null default now()
);
create index if not exists radar_heartbeat_recent on public.radar_heartbeat (observed_at_utc desc);
alter table public.radar_heartbeat enable row level security;
revoke all on public.radar_heartbeat from anon, authenticated;
revoke all on sequence public.radar_heartbeat_id_seq from anon, authenticated;
-- No RLS policies. Only the service role inserts; Task access needs a separate scoped read path.
