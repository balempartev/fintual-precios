# Verificación y límites observados

**Observación pública:** 2026-09-23 18:23 UTC (14:23 Nueva York). Esta tabla describe el flujo anterior, antes de publicar el nuevo código. [Listado de Actions](https://github.com/balempartev/fintual-precios/actions/workflows/precios.yml).

| Ejecución | Disparador | Hora visible en GitHub (GMT-3) | Duración | Resultado verificable |
|---|---|---|---|---|
| [#1](https://github.com/balempartev/fintual-precios/actions/runs/35779558868) | Manual | 22 sep 17:19 | 1m 6s | Éxito técnico; no prueba periodicidad. |
| [#2](https://github.com/balempartev/fintual-precios/actions/runs/35795409321) | Programado | 22 sep 20:02 | 7s | Guardia de horario pasó; consulta y publicación **omitidas**, según resumen de pasos del job. |
| [#3](https://github.com/balempartev/fintual-precios/actions/runs/35876789748) | Manual | 23 sep 11:47 | 1m 11s | Éxito técnico; no prueba periodicidad. |
| [#4](https://github.com/balempartev/fintual-precios/actions/runs/35880950101) | Manual | 23 sep 12:21 | 1m 1s | Éxito técnico. El archivo generado indica 15 tickers solicitados, 12 con operación y cotización IEX recientes; Nasdaq no disponible. |

Hasta las 14:23 NY del 23 de septiembre, GitHub mostraba **solo cuatro ejecuciones totales y una programada**. No hay evidencia de dos ejecuciones programadas consecutivas cada cinco minutos. Tampoco hay evidencia de escaneo de más de quince tickers en producción. El estado previo `OK_PARCIAL_RESEARCH_ONLY` era una comprobación de un grupo pequeño, no del universo de Fintual.

## Criterios de aceptación después de publicar

- Que al menos dos ejecuciones con disparador `schedule` sigan una a la otra durante la sesión, con fecha y diferencia de inicio registradas. Una ejecución `workflow_dispatch` no cuenta.
- Que `docs/estado.json` indique catálogo comprobado, cobertura por lote, hora de fin y fallos; contrastar `listed_candidates`, `fintual_links_verified` y `symbols_with_recent_iex_trade`.
- Que ninguna ruta pública contenga precios, porcentajes, volúmenes ni datos IEX por ticker. Confirmar el rechazo automático de historial mientras la visibilidad siga pública.
- Si se autoriza y valida almacenamiento privado, que `docs/precios.json` tenga horas individuales y que dos líneas sucesivas de `history/AAAA-MM-DD.jsonl` correspondan a ejecuciones distintas.
- Que un feriado o cierre anticipado omita la consulta si el reloj GET de Alpaca informa `is_open=false`.

**Estado de la versión preparada:** pruebas unitarias locales correctas; publicación y prueba de producción pendientes de autenticación/escritura. GitHub no garantiza la precisión ni la entrega de los cron; esos límites siguen vigentes aunque dos pruebas pasen.
