# Operación V13 — continuidad de V12

Actualizado: 29/09/2026. Este documento sustituye únicamente las referencias anteriores al origen del programador. No borra la evidencia histórica ni acredita éxito futuro.

## Programador instalado

Supabase pg_cron dispara precios.yml cada cinco minutos durante lunes-viernes NY09:30–16:00. El guard del workflow exige reloj Alpaca abierto, un slot con zona horaria y edad máxima de 240 segundos. Los cierres anticipados y feriados quedan bloqueados por el reloj. Cada disparo externo ejecuta un ciclo. Se retiró el schedule nativo del recolector para evitar dos programadores. El vigilante conserva su programación independiente.

GitHub registra event=workflow_dispatch también para estos disparos automáticos. Un título, HTTP 204 o un job verde por sí solos no prueban captura. La auditoría privada correlaciona slot de cron, respuesta aceptada, run de primer intento, paso de escaneo exitoso y estado generado. Las pruebas kind=validation y recuperaciones manuales no cuentan como producción.

El token limitado al repositorio se conserva en Vault. No debe copiarse al código, informes, navegador ni chat. La protección instalada detiene nuevos disparos el 28/10/2026 UTC si no se renueva de forma autorizada. El transporte privado usa HTTPS síncrono; las solicitudes autenticadas nuevas no guardan cabeceras en la cola compartida pg_net. Las respuestas privadas contienen solo resultados, nunca cabeceras de solicitud.

## Evidencia y consultas privadas

Las funciones radar-heartbeat v9 y radar-github-runs v3 se conservan. Sus métricas históricas de schedule nativo no prueban el nuevo origen. Las migraciones aplicadas y el registro remoto son la fuente de continuidad; no reaplicar scripts V12 ni versiones iniciales del transporte.

Consultas de operación, usando acceso backend autorizado:

~~~sql
select * from radar_scheduler.capture_evidence order by slot_utc desc limit 12;
select * from public.radar_external_daily_capture_audit;
select * from public.radar_report_freshness_gate;
select * from public.radar_report_delivery_daily;
select event_id, recorded_at_utc, summary, details
from public.radar_engineering_log order by recorded_at_utc desc limit 20;
~~~

El observador consulta cada minuto; la lectura del estado público añade un parámetro numérico de frescura para evitar que la caché devuelva la captura nocturna. Nunca envía credenciales al dominio raw.

Dos pruebas autónomas nocturnas finalizaron correctamente: runs 36508187270 y 36508589986, arranques 01:30:12Z y 01:35:10Z (298 segundos). No prueban frescura bursátil. El cron temporal se retiró automáticamente tras su límite. La primera captura bursátil del 29/09 fue run 36575536667, inicio13:30:14Z, generación13:31:51Z, con2442 operaciones IEX recientes. La aceptación de tres capturas depende de la vista privada; no se da por aprobada aquí antes de observarla.

## Vigilancia y nueve informes

vigilancia.py mantiene las comprobaciones de antigüedad, cobertura>=80%, operaciones recientes>0 y ningún lote fallido. Mantiene recuperación acotada a dos intentos diarios. Desde el cambio de programador indica EXTERNAL_AUDIT_REQUIRED para la apertura y remite a la auditoría privada; nunca convierte dispatch manual en evidencia automática. Los resultados nativos anteriores al29/09 se conservan.

Los informes esperados siguen siendo PRE09:15, H01–H07 a09:30–15:30 y CLOSE16:15, todos hora de Nueva York. La tarea horaria tenía default_timezone=America/Santiago aunque DTSTART indicaba Nueva York; se corrigió a America/New_York el29/09, conservando la misma tarea y sus siete horas. Es una causa plausible del disparo adelantado y H07 ausente, no una prueba retrospectiva de entrega.

El28/09 se verificaron ocho comprobantes de correo de nueve; H07 no apareció. Correo no equivale a publicación independiente ni a push. No fabricar el informe omitido ni marcar9/9 sin recibos. Las tareas dominicales conservan horario Chile.

## Límites preservados

Repositorio público: no publicar cotizaciones licenciadas, posiciones, saldos ni secretos. Conteos operativos no prueban precios individuales ni análisis fundamental de todo el universo. IEX no es mercado consolidado. El efectivo histórico no autoriza montos actuales. No hay ejecución de operaciones financieras. La interfaz privada y la entrega nativa de notificaciones requieren evidencia propia; el buen funcionamiento del recolector no las certifica.
