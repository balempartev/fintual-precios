# Evidencia fechada y criterios pendientes

## Auditoría previa al cambio, 24-09-2026 13:27 UTC

- GitHub `main` era `2fc23a2`; último `schedule` visible el 23/09 19:06 Chile saltó captura por sesión cerrada. Último barrido amplio manual [run 35906627707](https://github.com/balempartev/fintual-precios/actions/runs/35906627707), 23/09 19:04:07 UTC: 11.929 candidatos, 11.865 snapshots, 2.273 operaciones IEX recientes, 3.519 enlaces Fintual. Es evidencia de ayer, no precio actual.
- Existían cinco Tasks activas y tres antiguas inactivas con los nueve cortes laborales y dos domingos configurados. `next_run_time` era nulo en la API. El estado detallado de correos, recepciones y base del formulario es privado y no se publica en GitHub. La ejecución de una Task y la publicación de un mensaje siguen siendo pruebas distintas.

## Despliegue actual

- [Commit 02e5294](https://github.com/balempartev/fintual-precios/commit/02e52945c91969c71f18075a6a2081910e9a0161): cron UTC y job de vigilancia independientes.
- [Commit f441f89](https://github.com/balempartev/fintual-precios/commit/f441f89fe739b9413ed934037c33948c6563dda9): 11 pruebas; [run 36006388282](https://github.com/balempartev/fintual-precios/actions/runs/36006388282) `push` las pasó a 13:32:59 UTC y saltó correctamente el escaneo. Una prueba `push` no cuenta como captura programada.
- [Run 36006946546](https://github.com/balempartev/fintual-precios/actions/runs/36006946546), `workflow_dispatch` a las 13:38:55 UTC: 11.868 snapshots, 2.134 símbolos con operación IEX reciente, 3.519 enlaces Fintual. Es una captura real manual, no un `schedule`.
- [Run 36007268625](https://github.com/balempartev/fintual-precios/actions/runs/36007268625): vigilante manual sano e incidencia de prueba #1; correo GitHub recibido en INBOX. [Run 36008167854](https://github.com/balempartev/fintual-precios/actions/runs/36008167854): detectó edad 554 s, abrió [incidencia #2](https://github.com/balempartev/fintual-precios/issues/2) y solicitó recuperación con `GITHUB_TOKEN`. [Run 36008187443](https://github.com/balempartev/fintual-precios/actions/runs/36008187443), actor GitHub Actions bot, terminó exitosamente con 11.868 snapshots y dato generado 13:50:03 UTC. La incidencia llegó por correo.
- [Run 36009090485](https://github.com/balempartev/fintual-precios/actions/runs/36009090485) a 13:55:55 UTC: `HEALTHY` tras recuperación, `opening_acceptance=FAILED` porque cero eventos genuinos `schedule`, comentario de recuperación a #2 y correo recibido. El job rojo refleja la apertura fallida; no se debe pintar como éxito de cron.
- [Run 36010260691](https://github.com/balempartev/fintual-precios/actions/runs/36010260691): 14 pruebas de código tras añadir ventanas Chile y deduplicación de recordatorios. [Run 36010343487](https://github.com/balempartev/fintual-precios/actions/runs/36010343487): validación de tres ciclos `workflow_dispatch` iniciada; resultado pendiente al actualizar este documento.
- En Tasks, PRE y H01 del 24/09 se ejecutaron con alrededor de tres minutos de retraso. Sus dos comprobantes sin datos privados aparecen en Gmail SENT e INBOX. No existe prueba de publicación estable o push nativo desde esta superficie. Las otras siete entregas aún no se pueden certificar. Intentar crear dos Tasks para recordatorios 10:00/17:00 Chile y domingo 18:00 produjo la respuesta de plataforma `Your current plan allows only 5 scheduled tasks`; se conservan las cinco activas.

## Aceptación que no se debe anticipar

| Capacidad | Prueba exigida | Estado al redactar |
|---|---|---|
| Tres ciclos de cinco minutos | Tres `schedule` distintos, edad individual de datos y persistencia | FALLÓ la aceptación de apertura: cero eventos `schedule`; validación manual 3 ciclos en curso, que no la sustituye |
| Vigilante y recuperación | Run propio, diagnóstico, incidencia sintética y `dispatch` con recibo de finalización | PROBADO mediante runs manuales, bot, estado y correos; `schedule` del propio vigilante pendiente |
| Precios e historial privados legibles por Task | Recibos de dos ciclos y lectura desde el proceso programado, sin redistribución | BLOQUEADO por almacén privado/autorización de lectura compatible |
| Nueve informes con correo | Publicación y SENT+INBOX de nueve claves por día; push por dispositivo aparte | Verificar en canales privados; sin certificar 9/9 |
| Universo Fintual completo | Fuente Fintual oficial exhaustiva y cruce por identificador | 3.519 enlaces públicos, cobertura privada sin demostrar |

Actualizar los resultados con registros reales una vez existan. Un `last_run_time` y un correo no sustituyen el contenido de la conversación de la Task.
