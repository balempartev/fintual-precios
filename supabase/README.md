# Monitor independiente: instalación y límites verificados

Proyecto gratuito **radar-fintual**, referencia `ygrnkgzodjgofdgnztxg`,
[panel](https://supabase.com/dashboard/project/ygrnkgzodjgofdgnztxg),
instalado el 25-09-2026. Se aplicaron `migrations/202609250001_heartbeat.sql`
y `cron.sql`, se desplegó `radar-heartbeat` y se comprobó la inserción en
`public.radar_heartbeat`. El horario de los jobs queda en UTC:

| Job | Programación UTC | Función |
|---|---|---|
| `radar-heartbeat-5m` | `*/5 * * * *` | Inspecciona el estado público del radar y guarda una observación privada |
| `radar-heartbeat-retention` | `17 4 * * *` | Elimina observaciones de más de 90 días |

La URL del proyecto y un token aleatorio se guardaron en Vault; el mismo token
se guardó en secretos de la Edge Function. La función exige `Authorization: Bearer`
propio y no verifica el JWT heredado. Ninguno de los valores se guarda en GitHub.
La tabla tiene RLS sin políticas, con privilegios de tabla y secuencia revocados
a `anon` y `authenticated`; se verificó que ambos roles carecen de SELECT.
El rol de servicio inserta desde la función. Después de instalar el proyecto se
revocó además `EXECUTE` a `PUBLIC`, `anon` y `authenticated` sobre la función
`public.rls_auto_enable()` creada por la opción de RLS automático del panel.
El Security Advisor pasó de 2 advertencias a **0 errores / 0 advertencias**.

## Evidencia de ejecución

- Invocación manual autorizada 01:07:16 UTC: fila privada 1, respuesta HTTP 200,
  `OUTSIDE_REGULAR_WINDOW`.
- Cron a las 01:10:00 UTC: fila 2 a 01:10:01.658 UTC, status
  `OUTSIDE_REGULAR_WINDOW`; `cron.job_run_details` marcó `succeeded` y
  `net._http_response` dio HTTP 200.
- Cron a las 01:15 UTC: fila 3 a 01:15:01.110 UTC, mismo estado.
- La comprobación del tercer disparo consecutivo y las pruebas de apertura
  se documentan en `docs/PRUEBAS.md` cuando haya evidencia adicional.

Estos son **latidos automáticos del monitor**, no capturas de acciones cada cinco
minutos. El estado original de GitHub que leyeron las filas nocturnas correspondía
a una captura `workflow_dispatch` anterior; la columna `event` refleja ese origen,
no el desencadenante del propio cron de Supabase. Durante la próxima sesión NY,
`RECENT_SCHEDULED` exige evento `schedule`, edad <=480 segundos, >=80% snapshots,
al menos una transacción IEX reciente y ningún lote fallido. La ventana
09:30–16:00 NY es aproximada: no certifica festivos ni cierres anticipados.

El monitor solo conserva timestamps, identificador de ejecución, contadores y
errores del estado público. No almacena cotizaciones, formularios ni cartera;
su tabla privada no tiene aún una ruta de lectura para Tasks. Un cron exitoso y
un HTTP 200 tampoco certifican informe, correo, push ni recuperación de capturas.
El plan gratuito puede pausarse por inactividad; sus cuotas deben observarse.

Para revertir, desprogramar `radar-heartbeat-5m` y
`radar-heartbeat-retention`; después retirar la función y los secretos. El flujo
GitHub existente continúa en todo momento. La tabla puede conservarse para auditoría.
