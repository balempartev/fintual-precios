# Operación y recuperación sin intervención diaria

## Calendario

| Servicio | Hora esperada | Evidencia |
|---|---|---|
| Preapertura Task | L–V 09:15 NY | ejecución, publicación y correo se verifican por separado |
| Siete Task horarios | L–V 09:30–15:30 NY cada hora | siete claves de corte independientes; una ejecución atrasada es retrospectiva |
| Radar | L–V 09:32–15:57 NY cada cinco minutos aproximadamente | evento `schedule` + `docs/audit/fecha.jsonl` + `docs/estado.json` |
| Vigilante radar | L–V minutos UTC 06,16,26,36,46,56 de 13–21; domingos 21–22 UTC | `docs/vigilancia.json`, log diario, incidencia si hay falla; el cron aún requiere prueba real |
| Cierre Task | L–V 16:15 NY | auditoría de nueve hitos con cada evidencia |
| Formularios | L–V 10:00 y 17:00 Chile; domingo 18:00 Chile | formulario privado persistente; la vigilancia intenta avisar mediante incidencia GitHub entre minuto06 y24 de cada hora local indicada; el primer aviso `schedule` sigue pendiente de prueba |
| Domingos | 18:30 auditoría; 20:00 barrido Chile | tareas separadas |

## Estados que se pueden probar

1. Confirmar `schedule` en Actions, distinguirlo de `push` y `workflow_dispatch`. Un job verde que saltó el paso de exploración no es captura. Cada línea del registro tiene `run_id`, `event`, inicio, fin, conteos y fallos.
2. `docs/vigilancia.json` exige tres `run_id` programados distintos iniciados NY09:30–09:50, intervalos 180–420 segundos, al menos 80% de snapshots, alguna operación IEX reciente y ningún lote fallido. Si falla, el estado es `FAILED`, sin confundir un test manual de tres ciclos con puntualidad del cron.
3. En `STALE_OR_MISSING` con reloj Alpaca abierto, el vigilante solicita como máximo dos `workflow_dispatch` diarios separados por diez minutos. `DISPATCH_REQUESTED_NOT_COMPLETED` no certifica que terminó. Incidencia única por día; recepción de un aviso requiere evidencia externa. Fallo del reloj implica estado `UNKNOWN_CLOCK` y fallo conservador.
4. Cada informe Task necesita su propia prueba de ejecución, mensaje realmente publicado y comprobante Gmail SENT+INBOX con clave fecha/tipo/corte. Push en dispositivo es una cuarta prueba. Ni GitHub ni el formulario tienen API autorizada aquí para confirmar una publicación de Task ausente; el vigilante no puede recuperar ese informe por sí solo. Reejecuciones fuera de horario son retrospectivas.
5. Las cinco Tasks ocupan el límite de cinco tareas del plan: crear recordatorios independientes a las horas del formulario fue rechazado. La vigilancia GitHub crea como máximo una incidencia pública sin datos privados por fecha/hora chilena, con título único; su email asignado se probó en una incidencia técnica previa. El aviso no contiene posiciones ni el enlace privado. No confundirlo con la notificación nativa de ChatGPT. Los prompts de las cinco Tasks cruzan claves de recibos anteriores para intentar recuperación de informes omitidos verificables, sin tratar la falta de email como prueba suficiente de omisión.

## Respuesta automática y reversión

El job de vigilancia persiste diagnóstico incluso cuando el escaneo falla y emite una falla de job una vez por día para evitar decenas de correos repetidos; el JSON conserva el estado `FAILED` hasta que se cumplan criterios. Si el cron GitHub se omite, solicita una captura manual acotada; no reescribe hora de inicio ni afirma que sea `schedule`. Cuando comprueba otra captura, comenta una vez en la incidencia existente y ese comentario llega por email. Ver [arquitectura](ARQUITECTURA.md) y commits para revertir workflows; conservar las cinco Tasks antes de cambiar un horario o canal. Si una fuente primaria falla se registra en `primary_news_sources` y no se inventa una noticia. Si el catálogo falla, la cobertura parcial se marca explícitamente.

La operación automática depende de GitHub, Alpaca, fuentes públicas, Tasks y Gmail. El cierre del chat Work no detiene Actions o Tasks programadas; una indisponibilidad total de GitHub sí detiene tanto captura como vigilancia. El usuario no necesita editar YAML ni revisar logs: los enlaces de estado y los comprobantes son los canales previstos, con límites documentados.
