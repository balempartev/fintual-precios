# Operación y recuperación sin intervención diaria

## Calendario

| Servicio | Hora esperada | Evidencia |
|---|---|---|
| Preapertura Task | L–V 09:15 NY | ejecución, publicación y correo se verifican por separado |
| Siete Task horarios | L–V 09:30–15:30 NY cada hora | siete claves de corte independientes; una ejecución atrasada es retrospectiva |
| Radar | L–V 09:32–15:57 NY cada cinco minutos aproximadamente | evento `schedule` + `docs/audit/fecha.jsonl` + `docs/estado.json` |
| Vigilante radar | L–V minutos UTC 06,16,26,36,46,56 de 13–21 | `docs/vigilancia.json`, log diario, incidencia si hay falla |
| Cierre Task | L–V 16:15 NY | auditoría de nueve hitos con cada evidencia |
| Formularios | L–V 10:00 y 17:00 Chile; domingo 18:00 Chile | formulario persistente; recordatorios 10:15/17:15 y domingo 18:30, no a la hora exacta del formulario |
| Domingos | 18:30 auditoría; 20:00 barrido Chile | tareas separadas |

## Estados que se pueden probar

1. Confirmar `schedule` en Actions, distinguirlo de `push` y `workflow_dispatch`. Un job verde que saltó el paso de exploración no es captura. Cada línea del registro tiene `run_id`, `event`, inicio, fin, conteos y fallos.
2. `docs/vigilancia.json` exige tres `run_id` programados distintos iniciados NY09:30–09:50, intervalos 180–420 segundos, al menos 80% de snapshots, alguna operación IEX reciente y ningún lote fallido. Si falla, el estado es `FAILED`, sin confundir un test manual de tres ciclos con puntualidad del cron.
3. En `STALE_OR_MISSING` con reloj Alpaca abierto, el vigilante solicita como máximo dos `workflow_dispatch` diarios separados por diez minutos. `DISPATCH_REQUESTED_NOT_COMPLETED` no certifica que terminó. Incidencia única por día; recepción de un aviso requiere evidencia externa. Fallo del reloj implica estado `UNKNOWN_CLOCK` y fallo conservador.
4. Cada informe Task necesita su propia prueba de ejecución, mensaje realmente publicado y comprobante Gmail SENT+INBOX con clave fecha/tipo/corte. Push en dispositivo es una cuarta prueba. Ni GitHub ni el formulario tienen API autorizada aquí para confirmar una publicación de Task ausente; el vigilante no puede recuperar ese informe por sí solo. Reejecuciones fuera de horario son retrospectivas.

## Respuesta automática y reversión

El job de vigilancia persiste diagnóstico incluso cuando el escaneo falla y conserva el código de salida fallido. Si el cron GitHub se omite, solicita una captura manual acotada; no reescribe hora de inicio ni afirma que sea `schedule`. Ver [arquitectura](ARQUITECTURA.md) y commits para revertir workflows; conservar las cinco Tasks antes de cambiar un horario o canal. Si una fuente primaria falla se registra en `primary_news_sources` y no se inventa una noticia. Si el catálogo falla, la cobertura parcial se marca explícitamente.

La operación automática depende de GitHub, Alpaca, fuentes públicas, Tasks y Gmail. El cierre del chat Work no detiene Actions o Tasks programadas; una indisponibilidad total de GitHub sí detiene tanto captura como vigilancia. El usuario no necesita editar YAML ni revisar logs: los enlaces de estado y los comprobantes son los canales previstos, con límites documentados.
