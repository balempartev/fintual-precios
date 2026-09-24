# Radar Fintual · resumen ejecutivo, 24-09-2026

## Resultado observado

El radar en `main` escaneó 11.936 símbolos candidatos durante la sesión NY. En la captura manual del 24/09 a las 19:09:46 UTC persistió 11.872 snapshots Alpaca **IEX** y 1.996 símbolos con operación reciente. Los directorios bursátiles no prueban que un activo pueda comprarse en la cuenta Fintual: se verificaron 3.519 enlaces públicos Fintual; su página de ayuda anuncia más de 11.000, pero no entrega aquí una lista exhaustiva verificable. Se comprobaron [etiquetas por empresa](sectores.json) para 12 fichas Fintual, incluidas VICR, VKTX e IONQ; las otras 3.507 fichas verificadas aún no están clasificadas. [Estado vivo](estado.json), [auditoría diaria](audit/2026-09-24.jsonl), [catálogo](catalogo.json).

GitHub Actions pasó 16 pruebas remotas; 17 locales después del último cambio. La vigilancia manual detectó un barrido atrasado, abrió [incidencia #2](https://github.com/balempartev/fintual-precios/issues/2), disparó una captura que acabó con éxito y publicó comentario de recuperación; los correos llegaron al propietario. La **aceptación de tres ciclos `schedule` de apertura FALLÓ**: hubo cero. Solo apareció [uno tardío a las 17:56 UTC](https://github.com/balempartev/fintual-precios/actions/runs/36037739383). La recuperación simultánea falló por conflicto al publicar; esa carrera ya fue corregida y probada con capturas manuales. Un nuevo puente de seis ciclos por `schedule` espera su primera prueba automática. [Pruebas](PRUEBAS.md).

Las cinco tareas existentes conservan preapertura, siete cortes horarios, cierre y dos domingos, sin duplicar informes. Se observaron PRE y H01 del 24/09 con comprobantes SENT+INBOX; publicación estable y push del dispositivo no se pudieron comprobar. El formulario privado tiene dos confirmaciones reales guardadas en su base y las dos tareas observadas lo leyeron. La plataforma rechazó crear recordatorios Tasks adicionales: máximo cinco tareas. La vigilancia de GitHub contiene avisos limitados cerca de 10:00 y 17:00 Chile laborables y domingo 18:00; el primer disparo de ese cron aún no se ha observado. La cartera no figura en el repositorio.

Coste nuevo contratado: **USD 0**. No se enviaron órdenes bursátiles. No se publicaron cotizaciones IEX ni secretos. El repositorio público conserva enlaces, conteos técnicos y noticias oficiales; los precios por símbolo y su historia **no están accesibles a las tareas**, porque aún no hay almacén privado compatible y autorizado para ese flujo.

## Estado de los treinta problemas del dossier

Las referencias P01–P30 siguen la numeración original. `PROBADO` significa solo la parte descrita; `PENDIENTE` incluye un despliegue sin aceptación observada.

| ID | Estado | Evidencia o límite concreto |
|---|---|---|
| P01 | PENDIENTE | Cron UTC instalado; un `schedule` tardío; apertura fallida; puente desplegado sin prueba automática. |
| P02 | PARCIAL | Tres ciclos internos consecutivos probados; solo un `schedule` real tardío. |
| P03 | PARCIAL | 11.936 candidatos; 3.519 enlaces Fintual, sin catálogo oficial exhaustivo. |
| P04 | PARCIAL | Trade/quote con timestamp individual y pruebas; el repositorio público no entrega las filas. |
| P05 | PROBADO | Feed etiquetado IEX, sin confundirlo con SIP/NBBO. |
| P06 | BLOQUEADO | Sin lectura privada legal de precios por Task. |
| P07 | BLOQUEADO | Historial de precios desactivado mientras el repositorio sea público. |
| P08 | PENDIENTE | SEC 403 desde runner; fallback limitado no produce filings nuevos. |
| P09 | PARCIAL | Feeds primarios Fed/FDA probados; IR empresarial incompleto. |
| P10 | PARCIAL | Doce fichas Fintual con etiquetas individuales comprobadas; 3.507 pendientes y etiquetas no GICS. |
| P11 | PARCIAL | Ranking alzas, bajas y actividad IEX en memoria; RVOL20d y liquidez consolidada ausentes. |
| P12 | PARCIAL | Cinco reglas activas; PRE/H01 observados tarde, nueve diarios sin certificar. |
| P13 | PROBADO | Copia previa, cinco actualizaciones de continuidad y comparación posterior de reglas. |
| P14 | BLOQUEADO | Flags nativos anteriores false/false; autenticación de ChatGPT y recibo push pendientes. |
| P15 | PARCIAL | Dos comprobantes programados y correos GitHub de incidencias recibidos; no 9/9. |
| P16 | BLOQUEADO | Sin API autorizada de publicaciones de Tasks para vigilancia externa. |
| P17 | PARCIAL | H02 y H03 recuperados retrospectivamente con correos; publicación original y push sin prueba. |
| P18 | PARCIAL | Formulario real guardó dos confirmaciones y Task leyó dos; envío de prueba `is_test=1` pendiente. |
| P19 | PARCIAL | Formulario permanente; avisos Chile programados en vigilancia, cron sin prueba. |
| P20 | PARCIAL | Auditoría pública persistida; inteligencia y precios privados entre tareas no resueltos. |
| P21 | PENDIENTE | Comparación documentada, sin sustituto autenticado probado; GitHub se conserva. |
| P22 | PARCIAL | Actions no consume créditos Work; cron aún no aceptado. |
| P23 | PROBADO | Salida pública sin mercado IEX por ticker ni claves. |
| P24 | PENDIENTE | Matriz de aceptación registra apertura fallida, no declara 9/9. |
| P25 | PENDIENTE | Investigación independiente en prompts; calidad de siete informes aún no verificada. |
| P26 | PROBADO | Sin nuevas compras de servicios, permisos bursátiles ni órdenes. |
| P27 | PARCIAL | Fed/FDA con tres feeds activos; SEC e IR no cubiertos totalmente. |
| P28 | PENDIENTE | Cadena de comprobantes entre Tasks configurada; recuperación real de informe omitido no probada. |
| P29 | PARCIAL | [Runbook](RUNBOOK.md), alerta idempotente y reversión; cron externo pendiente. |
| P30 | PROBADO | Brechas y pruebas negativas publicadas en [PRUEBAS](PRUEBAS.md). |

## Decisión y reversión

Conservar temporalmente GitHub Actions + Alpaca Basic IEX + cinco Tasks + Gmail + formulario Sites. Cumple barrido técnico amplio a coste nuevo cero y evita publicar mercado licenciado; falla por ahora en puntualidad de `schedule`, historial privado y entrega comprobable de nueve informes. Massive Basic ofrece datos retrasados y 5 llamadas/min, Alpha Vantage 25 llamadas/día y Workers Free tiene límites de CPU y subconsultas que impiden asumir que sustituya este barrido sin partición ni pruebas. [Matriz de arquitectura](ARQUITECTURA.md), [contrato](CONTRATO_DATOS.md), [reversión](RUNBOOK.md). No cortar el repositorio ni las cinco tareas antes de ejecutar el sustituto en paralelo y aceptar sus datos y recibos.
