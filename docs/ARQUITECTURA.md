# Arquitectura y decisión, 24-09-2026

## Cadena efectivamente desplegada

1. `precios.yml` intenta una captura cada cinco minutos desde 09:32 hasta 15:57 NY. El cron cubre en UTC ambos cambios de horario y el paso `Verificar sesión` usa hora NY y `GET /v2/clock` de Alpaca. Un evento `push` ejecuta pruebas y omite el escaneo. Un `workflow_dispatch` puede probarlo sin dar por válida una ejecución programada.
2. `actualizar_precios.py` cruza los directorios Nasdaq y Other Listed con enlaces públicos Fintual, consulta snapshots Alpaca Basic por lotes y vuelve a consultar los destacados. Publica conteos, trazas y enlaces primarios, nunca cotizaciones por símbolo mientras el repositorio sea público. `docs/estado.json` declara fecha, feed, cobertura, fallos y si el historial privado está habilitado.
3. `vigilancia.yml`, en un job separado, observa la edad del último barrido, conserva un registro y limita a dos intentos de recuperación por día. Sus incidentes GitHub se asignan al propietario. Sigue dependiendo de GitHub: no vigila los informes de ChatGPT.
4. Las cinco tareas existentes preparan nueve informes laborables y dos entregas dominicales. Consultan la auditoría pública de GitHub, fuentes independientes y, cuando Sites está disponible dentro de la tarea, la última confirmación privada del formulario. Envían comprobantes sin datos financieros a la cuenta propia mediante Gmail, con clave única y búsqueda previa. Un comprobante no prueba publicación ni push.
5. El formulario privado está alojado en un proyecto Sites separado con base `confirmations`; el contenido de esa base no pertenece a este repositorio público.

## Selección comprobable de infraestructura

| Opción | Capacidad observada o publicada | Brecha material | Decisión |
|---|---|---|---|
| GitHub Actions + Alpaca Basic | Credenciales y ejecución manual ya probadas; universo bursátil amplio; IEX en tiempo real, 200 consultas históricas/min; GitHub admite mínimo cinco minutos | `schedule` puede atrasarse o descartarse; no se pueden redistribuir precios Alpaca; no hay canal privado de lectura de precios en Tasks | Conservar el escaneo y vigilarlo. No afirmar cinco minutos garantizados |
| Cloudflare Workers Free + Cron + D1 | Cron y almacenamiento gestionados, sin servidor propio | CPU gratuita 10 ms por disparo programado, 50 subconsultas externas por invocación; escaneo de miles requiere partición, servicio nuevo y permisos | Candidato de sustitución; sin despliegue ni corte de GitHub hasta validar cuota, autorización y lectura privada |
| VPS con cron | Control de horario y almacenamiento | Administración del servidor, coste habitual y credenciales nuevas | No seleccionado para requisito de mínimo mantenimiento y sin gasto |
| Otros proveedores gratuitos por símbolo | Pueden corroborar manualmente candidatas | Cuotas o retraso insuficientes para ~12.000 símbolos cada cinco minutos; verificar plan actual antes de asumir cobertura | Fuentes complementarias, no reemplazo validado |
| Datos consolidados SIP de Alpaca | Más bolsas y volumen que IEX | Suscripción pagada; licencia de redistribución independiente | No contratado |
| Tasks + Gmail + Sites | Tareas, correo propio y formulario ya conectados; primer comprobante automático observado el 24/09 | Sin recibo externo de publicación/push de cada Task ni lectura privada de precios IEX en tarea | Mantener cinco tareas; separar evidencia de ejecución, mensaje, correo y dispositivo |

Fuentes: [sintaxis y zona GitHub](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule), [eventos atrasados/omitidos](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule), [Alpaca Basic](https://docs.alpaca.markets/us/docs/about-market-data-api), [restricción de redistribución](https://alpaca.markets/support/redistribute-alpaca-api), [límites Workers](https://developers.cloudflare.com/workers/platform/limits/), [Tasks y notificaciones](https://help.openai.com/en/articles/10291617-tasks-in-chatgpt). La antigua regla con `timezone: America/New_York` era **sintaxis admitida** por GitHub; el cambio a UTC es una simplificación operativa, no una solución probada a los retrasos del proveedor.

## Reversión

Guardar commit anterior a los workflows `2fc23a2b8dac1a9b2f05923b63c13ad86fc1bf9a` y el primer commit de workflows `02e52945c91969c71f18075a6a2081910e9a0161`. Un cambio a otro ejecutor deberá ejecutarse en paralelo y probar tres capturas y lectura por informes antes de apagar GitHub. Las cinco Tasks y sus copias de seguridad se conservan.
