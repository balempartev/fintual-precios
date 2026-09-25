# Monitor independiente: estado de instalación

El código está preparado y sus reglas tienen pruebas locales. **No hay proyecto Supabase,
migración, función ni cron verificados hasta observarlos en el servicio conectado.**
Conservar GitHub Actions y las cinco Tasks mientras tanto.

## Instalación controlada

1. Elegir un proyecto Supabase existente autorizado o crear uno gratuito sin introducir
   datos de pago. Aplicar `migrations/202609250001_heartbeat.sql`.
2. Generar un secreto aleatorio nuevo de 32 bytes, guardarlo como secreto de función
   `RADAR_HEARTBEAT_TOKEN` y en Vault como `radar_heartbeat_token`; guardar la URL
   del proyecto en Vault como `radar_project_url`. Nunca registrar ni exponer los valores.
3. Desplegar `functions/radar-heartbeat` con `verify_jwt = false` en `config.toml`.
   El servidor exige `Authorization: Bearer <secreto>` antes de llamar al origen.
4. Invocar una vez desde un cliente autorizado y comprobar fila y estado.
   Aplicar `cron.sql` solo tras esa comprobación. Verificar tres filas originadas
   por tres invocaciones automáticas a minutos separados por cinco, junto con
   `cron.job_run_details` y las respuestas de `net._http_response`.
5. Comprobar siguiente apertura NY con el mercado abierto: `RECENT_SCHEDULED`
   exige evento `schedule`, edad <=480 segundos, >=80% snapshots, alguna operación
   IEX reciente y cero lotes fallidos. Ningún manual acredita cron.

El monitor solo registra horas, ID de run, contadores y errores del estado público.
No almacena cotizaciones, formularios ni cartera; las lecturas `anon` y
`authenticated` están denegadas. La ventana 09:30–16:00 NY es una aproximación:
el monitor no certifica festivos ni cierre temprano (`market_clock_verified=false`).
Un cron exitoso y un HTTP 2xx no prueban entrega de informes, email ni push.
El proyecto gratuito puede pausarse por inactividad y sus cuotas deben observarse.

Para revertir, desprogramar `radar-heartbeat-5m` y
`radar-heartbeat-retention`; luego retirar la función y los secretos. El flujo
GitHub existente continúa en todo momento. La tabla puede conservarse para auditoría.
