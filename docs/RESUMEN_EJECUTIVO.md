# Radar Fintual · resumen ejecutivo, 24-09-2026

## Resultado observado

El radar en `main` escaneó 11.936 símbolos candidatos durante la sesión NY. En la tercera captura, a las 14:17:53 UTC, persistió 11.869 snapshots Alpaca **IEX** y 2.249 símbolos con operación de los últimos 150 segundos. Los directorios bursátiles no prueban que un activo pueda comprarse en la cuenta Fintual: se verificaron 3.519 enlaces públicos Fintual; su página de ayuda anuncia más de 11.000, pero no entrega aquí una lista exhaustiva verificable. [Estado vivo](estado.json), [auditoría diaria](audit/2026-09-24.jsonl), [catálogo con procedencia](catalogo.json).

GitHub Actions pasó 14 pruebas de código. La vigilancia manual detectó un barrido atrasado, abrió [incidencia #2](https://github.com/balempartev/fintual-precios/issues/2), disparó una captura que acabó con éxito y publicó comentario de recuperación; los correos de incidencia y recuperación se recibieron en la cuenta del propietario. La **aceptación de tres disparos `schedule` de apertura FALLÓ**: hubo cero. Tres ciclos del mismo `workflow_dispatch` comenzaron a las 14:06:21, 14:11:21 y 14:16:21 UTC (300 segundos exactos); los tres persistieron 11.869 snapshots, sin lotes fallidos. Prueban motor y cadencia interna, nunca el cron externo. [Pruebas](PRUEBAS.md).

Las cinco tareas existentes conservan preapertura, siete cortes horarios, cierre y dos domingos, sin duplicar informes. Se observaron PRE y H01 del 24/09 con comprobantes SENT+INBOX; publicación estable y push del dispositivo no se pudieron comprobar. El formulario privado tiene dos confirmaciones reales guardadas en su base y las dos tareas observadas lo leyeron. La plataforma rechazó crear recordatorios Tasks adicionales: máximo cinco tareas. La vigilancia de GitHub contiene avisos limitados cerca de 10:00 y 17:00 Chile laborables y domingo 18:00; el primer disparo de ese cron aún no se ha observado. La cartera no figura en el repositorio.

Coste nuevo contratado: **USD 0**. No se enviaron órdenes bursátiles. No se publicaron cotizaciones IEX ni secretos. El repositorio público conserva enlaces, conteos técnicos y noticias oficiales; los precios por símbolo y su historia **no están accesibles a las tareas**, porque aún no hay almacén privado compatible y autorizado para ese flujo.

## Estado de los treinta problemas del dossier

Las referencias P01–P30 siguen la numeración original. `PROBADO` significa solo la parte descrita; `PENDIENTE` incluye un despliegue sin aceptación observada.

| ID | Estado | Evidencia o límite concreto |
|---|---|---|
| P01 | PENDIENTE | Cron UTC instalado; apertura `schedule` fallida. |
| P02 | PARCIAL | Tres ciclos internos consecutivos probados; cero `schedule` real. |
| P03 | PARCIAL | 11.936 candidatos; 3.519 enlaces Fintual, sin catálogo oficial exhaustivo. |
| P04 | PARCIAL | Trade/quote con timestamp individual y pruebas; el repositorio público no entrega las filas. |
| P05 | PROBADO | Feed etiquetado IEX, sin confundirlo con SIP/NBBO. |
| P06 | BLOQUEADO | Sin lectura privada legal de precios por Task. |
| P07 | BLOQUEADO | Historial de precios desactivado mientras el repositorio sea público. |
| P08 | PENDIENTE | SEC 403 desde runner; fallback limitado no produce filings nuevos. |
| P09 | PARCIAL | Feeds primarios Fed/FDA probados; IR empresarial incompleto. |
| P10 | PARCIAL | Once ETF sectoriales comprobados; empresas individuales sin sector verificable. |
| P11 | PARCIAL | Ranking alzas, bajas y actividad IEX en memoria; RVOL20d y liquidez consolidada ausentes. |
| P12 | PARCIAL | Cinco reglas activas; PRE/H01 observados tarde, nueve diarios sin certificar. |
| P13 | PROBADO | Copia previa, cinco actualizaciones de continuidad y comparación posterior de reglas. |
| P14 | BLOQUEADO | Flags nativos anteriores false/false; autenticación de ChatGPT y recibo push pendientes. |
| P15 | PARCIAL | Dos comprobantes programados y correos GitHub de incidencias recibidos; no 9/9. |
| P16 | BLOQUEADO | Sin API autorizada de publicaciones de Tasks para vigilancia externa. |
| P17 | PENDIENTE | Regla retrospectiva escrita; entrega recuperada aún no observada. |
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
