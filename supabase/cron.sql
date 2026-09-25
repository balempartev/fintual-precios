-- Install after the Edge Function is deployed and BOTH Vault entries exist:
-- radar_project_url = https://<project-ref>.supabase.co
-- radar_heartbeat_token = the same random token stored in the function secret.
-- No literal token or service-role key belongs in this repository or cron.job.
create schema if not exists extensions;
create extension if not exists pg_cron;
create extension if not exists pg_net with schema extensions;

select cron.schedule('radar-heartbeat-5m', '*/5 * * * *', $job$
  select net.http_post(
    url := (select decrypted_secret from vault.decrypted_secrets
             where name = 'radar_project_url') || '/functions/v1/radar-heartbeat',
    headers := jsonb_build_object(
      'content-type', 'application/json',
      'authorization', 'Bearer ' ||
        (select decrypted_secret from vault.decrypted_secrets
         where name = 'radar_heartbeat_token')
    ),
    body := '{}'::jsonb,
    timeout_milliseconds := 10000
  ) as request_id;
$job$);

select cron.schedule('radar-heartbeat-retention', '17 4 * * *', $job$
  delete from public.radar_heartbeat
  where observed_at_utc < now() - interval '90 days';
$job$);
