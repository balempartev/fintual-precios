# Evidencia fechada y criterios pendientes

## Auditoría previa al cambio, 24-09-2026 13:27 UTC

- GitHub `main` era `2fc23a2`; último `schedule` visible el 23/09 19:06 Chile saltó captura por sesión cerrada. Último barrido amplio manual [run 35906627707](https://github.com/balempartev/fintual-precios/actions/runs/35906627707), 23/09 19:04:07 UTC: 11.929 candidatos, 11.865 snapshots, 2.273 operaciones IEX recientes, 3.519 enlaces Fintual. Es evidencia de ayer, no precio actual.
- Existían cinco Tasks activas y tres antiguas inactivas con los nueve cortes laborales y dos domingos configurados. `next_run_time` era nulo en la API. El estado detallado de correos, recepciones y base del formulario es privado y no se publica en GitHub. La ejecución de una Task y la publicación de un mensaje siguen siendo pruebas distintas.

## Despliegue actual

- [Commit 02e5294](https://github.com/balempartev/fintual-precios/commit/02e52945c91969c71f18075a6a2081910e9a0161): cron UTC y job de vigilancia independientes.
- [Commit f441f89](https://github.com/balempartev/fintual-precios/commit/f441f89fe739b9413ed934037c33948c6563dda9): 11 pruebas; [run 36006388282](https://github.com/balempartev/fintual-precios/actions/runs/36006388282) `push` las pasó a 13:32:59 UTC y saltó correctamente el escaneo. Una prueba `push` no cuenta como captura programada.

## Aceptación que no se debe anticipar

| Capacidad | Prueba exigida | Estado al redactar |
|---|---|---|
| Tres ciclos de cinco minutos | Tres `schedule` distintos, edad individual de datos y persistencia | PENDIENTE en apertura actual |
| Vigilante y recuperación | Run propio, diagnóstico, incidencia sintética y `dispatch` con recibo de finalización | PENDIENTE de ejecución real |
| Precios e historial privados legibles por Task | Recibos de dos ciclos y lectura desde el proceso programado, sin redistribución | BLOQUEADO por almacén privado/autorización de lectura compatible |
| Nueve informes con correo | Publicación y SENT+INBOX de nueve claves por día; push por dispositivo aparte | Verificar en canales privados; sin certificar 9/9 |
| Universo Fintual completo | Fuente Fintual oficial exhaustiva y cruce por identificador | 3.519 enlaces públicos, cobertura privada sin demostrar |

Actualizar los resultados con registros reales una vez existan. Un `last_run_time` y un correo no sustituyen el contenido de la conversación de la Task.
