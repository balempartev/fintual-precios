# Radar Fintual autónomo

Explora acciones y ETF estadounidenses en modo de **solo lectura**. No tiene funciones para operar, leer saldos, ni gestionar posiciones. Está programado para intentar capturas cada cinco minutos durante la sesión ordinaria de Nueva York. La periodicidad intradía aún debe superar la prueba automática de apertura; GitHub Actions puede retrasar o descartar ejecuciones.

## Qué puede comprobar

1. [Fintual informa más de 11.000 activos](https://ayuda.fintual.cl/es/articles/8592794-todas-las-acciones-etfs-disponibles-en-fintual) desde la ampliación de 2026. Su lista de enlaces individuales es una prueba pública para un subconjunto, pero ni esa lista ni un ticker listado demuestran que la cuenta de un usuario pueda operarlo. No se inicia sesión en Fintual.
2. Los archivos oficiales [Nasdaq Listed y Other Listed](https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs) proporcionan candidatos de varias bolsas, con la marca ETF. Se descartan instrumentos que se puedan reconocer como derechos, warrants, unidades, preferentes, bonos y notas. Los restantes no son necesariamente todos instrumentos elegibles en Fintual. Se incorporan además los enlaces Fintual ausentes del directorio como `FINTUAL_LINK_ONLY`, sin afirmar vigencia de listado o comprabilidad. Se recorren todos los candidatos, sin filtrar industrias o sectores. Estas fuentes no incluyen una taxonomía sectorial completa: `sector_classification_complete=false` y los destacados aparecen como `UNCLASSIFIED` hasta contar con una fuente comprobable.
3. El plan Basic de [Alpaca](https://docs.alpaca.markets/us/docs/about-market-data-api) ofrece datos IEX gratis y hasta 200 llamadas por minuto. IEX es **una sola bolsa**, no precio, spread ni volumen consolidado de todas las bolsas. Cada operación y cotización lleva su propia hora. La búsqueda de alzas y bajas usa la última operación IEX con menos de 150 segundos respecto de la publicación y el cierre anterior del mismo feed. La actividad anormal es solo un indicador aproximado: volumen IEX acumulado dividido por el volumen IEX del día anterior, ajustado por la fracción transcurrida de la sesión; no es un RVOL de veinte días ni una señal de liquidez global.
4. Para hasta doce símbolos destacados se buscan presentaciones recientes en [SEC EDGAR](https://www.sec.gov/about/developer-resources): formularios 8-K, 6-K, 10-Q y 10-K, con enlaces a los documentos primarios. Un documento reciente **no prueba** que explique un movimiento. No hay cobertura exhaustiva de comunicados de prensa, noticias sectoriales ni ETF.

## Publicación y licencia

[Alpaca dice expresamente que sus datos de API no pueden redistribuirse](https://alpaca.markets/support/redistribute-alpaca-api). Este repositorio nació **público**. Mientras siga público:

- `docs/audit/AAAA-MM-DD.jsonl`: historial operativo por ejecución (sin cotizaciones), con identificador del run y disparador.
- [docs/estado.json](docs/estado.json): hora de ejecución, conteos de cobertura, fallos por lote, advertencias y enlaces SEC; sin precios, porcentajes, volumen ni ranking de símbolos derivados de cotizaciones.
- [docs/catalogo.json](docs/catalogo.json): ticker, bolsa, tipo y enlaces verificados de Fintual obtenidos de páginas públicas, con fecha y advertencias.
- [docs/precios.json](docs/precios.json): marca explícita de que los datos de mercado no se publican.
- [docs/lectura_rapida.md](docs/lectura_rapida.md): lectura breve del estado, sin cotizaciones.

Estas rutas son accesibles a informes independientes. Consulta la hora y los fallos antes de describir un dato como actual. URL de estado: https://raw.githubusercontent.com/balempartev/fintual-precios/main/docs/estado.json .

El código tiene un modo privado: **solo si GitHub indica que el repositorio es privado**, [docs/precios.json](docs/precios.json) muestra los destacados y sus horas individuales, y `history/AAAA-MM-DD.jsonl` conserva una línea por ejecución con esos destacados. El historial guarda los mejores candidatos y símbolos prioritarios, **no todos los miles de snapshots en cada ciclo**. El tamaño queda acotado. No cambies el indicador de visibilidad en un archivo: procede del evento de GitHub. La transición a privado exige comprobar cómo accederán los informes horarios; las URL públicas dejarían de servir.

Los commits históricos anteriores a este cambio contenían cotizaciones IEX. Quitar los archivos del commit actual no borra los commits anteriores. Un saneamiento total exigiría reescribir la historia y coordinar los consumidores; no se fuerza aquí.

## Horarios, errores y operación

El cron usa una ventana UTC 13:02–20:57, cada cinco minutos, que cubre ambos regímenes DST; el guard usa `America/New_York` y el reloj de mercado. Durante sesión ordinaria corresponde a NY09:32,09:37…15:57. Antes de consultar, una solicitud **GET** al reloj de mercado de Alpaca confirma que la sesión está abierta, incluidos feriados y cierres anticipados. Si falla el reloj, no se consulta el mercado. `workflow_dispatch` permite una prueba manual incluso fuera de horario. `push` ejecuta pruebas locales sin explorar el mercado.

El escaneo divide el universo en lotes de 75 y refresca al final los candidatos destacados. El catálogo se comprueba una vez por fecha NY si las tres fuentes responden; los fallos se reintentan; si fallan las fuentes se conserva el último catálogo completo, o se recurre a la base histórica parcial de 2.090 símbolos, **marcando cobertura incompleta**. Si un lote falla se registra `batch_start` y `error`; una ejecución sin ningún snapshot devuelve error y no finge precios recientes. Los archivos de estado se actualizan al terminar una consulta; las edades se vuelven a calcular antes de publicar.

GitHub admite un intervalo mínimo de cinco minutos, pero [advierte retrasos, ejecuciones omitidas y desactivación tras 60 días sin actividad en repositorios públicos](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule). Cada consulta tiene un límite de cuatro minutos. El flujo admite una prueba controlada `validation_cycles=3` con tres ciclos que arrancan cada 300 segundos y persisten separadamente; su límite total es dieciséis minutos. Los eventos `schedule` ejecutan un solo ciclo. Una prueba de tres ciclos iniciada manualmente **no** demuestra puntualidad del cron. Un segundo workflow de vigilancia comprueba frescura cada diez minutos, solicita hasta dos recuperaciones diarias y abre incidencias técnicas. Comparte GitHub: no protege ante una caída total de GitHub ni confirma publicaciones o push de Tasks.

Secretos ya utilizados por el flujo: `ALPACA_API_KEY_ID` y `ALPACA_API_SECRET_KEY`. No se muestran ni se guardan sus valores. Los únicos destinos de las credenciales son las consultas GET de datos IEX y el reloj de mercado paper. El código usa biblioteca estándar Python 3.11; las pruebas no requieren red:

```bash
python -m unittest discover -s tests -v
```

## Opciones estudiadas

| Fuente / arquitectura | Alcance sin contratar | Limitación que importa | Decisión |
|---|---|---|---|
| [Alpaca Basic](https://docs.alpaca.markets/us/docs/about-market-data-api) + Actions | IEX en tiempo real, lotes de snapshots y 200 solicitudes/min | Cobertura y volumen solo IEX; prohíbe redistribución pública | Escaneo interno; precios e historial solo con repositorio privado |
| [Massive Basic](https://massive.com/pricing) | Datos con 15 minutos de retraso y cinco solicitudes/min | No cubre este radar casi inmediato, ni servicio ya conectado | No contratar ni depender de ello |
| [Twelve Data Basic](https://twelvedata.com/pricing) | Créditos gratuitos limitados; confirmar cuota antes de crear cuenta | Insuficiente para miles de símbolos cada cinco minutos; requiere cuenta nueva | No seleccionado |
| [Alpha Vantage gratis](https://www.alphavantage.co/support/) | 25 solicitudes al día en plan estándar | Insuficiente para escaneo intradía amplio; excepciones requieren verificación del proveedor | No seleccionado |
| [Cloudflare Workers Free + Cron](https://developers.cloudflare.com/workers/platform/limits/) | 100.000 solicitudes entrantes/día | 50 subsolicitudes externas por invocación y 10 ms CPU; exige dividir escaneo, autenticación nueva y validar almacenamiento/lectura privados | Alternativa pendiente si el cron de Actions no cumple; no reemplazar sin prueba |
| VPS con cron | Proceso persistente y horario controlable | Servidor, actualizaciones, monitoreo y normalmente costo mensual | Mayor mantenimiento; no seleccionado |
| Nasdaq Screener web | Puede mostrar cambios amplios | Falló en las ejecuciones anteriores, a veces no aporta `asOf`; no es API pública confiable para este fin | Sustituido por directorios oficiales **solo para símbolos** |
| Nasdaq Symbol Directory + SEC EDGAR | Listados y documentos primarios públicos | No son cotizaciones ni verifican la cuenta Fintual | Catálogo, cobertura y vínculos a documentos |
| GitHub Actions + archivos versionados | Infraestructura ya existente, historial consultable | Cron aproximado y crecimiento del historial; repositorio público incompatible con publicar API prices | Se conserva, con barrera de privacidad automática |

**Verificación de producción:** [docs/PRUEBAS.md](docs/PRUEBAS.md) reúne las evidencias de la sesión actual; [docs/VERIFICACION.md](docs/VERIFICACION.md) conserva la auditoría histórica. Los tests locales comprueban lógica y bloqueo de publicación; no sustituyen ejecuciones automáticas consecutivas.

## Ampliación V5 nocturna

- `fuentes_primarias.py`: RSS oficiales FDA y Federal Reserve, con URL, fecha de publicación cuando existe, fecha de consulta y errores. Archivo público `docs/catalizadores.json`. No implica que cada noticia explique un movimiento. SEC añade formularios de financiación y consulta documentada de CIK de tres emisores si falla el mapa; comprueba el ticker devuelto. No es cobertura exhaustiva de IR.
- Once ETF de referencia sectorial se cruzan con catálogo y Fintual. Las acciones individuales permanecen sin taxonomía completa.
- `vigilancia.py` y `.github/workflows/vigilancia.yml`: comprobación independiente del job de captura, dos reintentos máximos por fecha NY separados al menos diez minutos, incidencias idempotentes y conservación del estado. No usa créditos de Work.
- Aceptación diaria de apertura: exige tres `run_id` diferentes con evento `schedule`, arranques NY09:30–09:50, intervalos180–420s, >=80% snapshots, alguna operación individual reciente y ningún lote fallido. Tres ciclos manuales no sirven como prueba de cron.
- Mantiene `docs/vigilancia.json`, `docs/vigilancia/AAAA-MM-DD.jsonl` y `docs/recovery_state.json`. Los avisos por incidencia solo prueban recepción cuando hay evidencia fuera de GitHub.
- El formulario privado vive en un servicio separado; sus datos y configuraciones privadas de Tasks no se guardan en este repositorio público.

Documentación detallada: [resumen ejecutivo](docs/RESUMEN_EJECUTIVO.md), [arquitectura](docs/ARQUITECTURA.md), [operación](docs/RUNBOOK.md), [contrato](docs/CONTRATO_DATOS.md), [pruebas](docs/PRUEBAS.md) y [cambios](docs/CAMBIOS.md). El inventario de IDs y prompts de las cinco tareas se conserva en un archivo privado aparte.

**Pruebas del 24/09:** [14 tests remotos](https://github.com/balempartev/fintual-precios/actions/runs/36010260691); [tres capturas manuales consecutivas](https://github.com/balempartev/fintual-precios/actions/runs/36010343487) iniciadas 14:06:21,14:11:21,14:16:21 UTC, con 11.869 snapshots IEX por ciclo y 2.223/2.232/2.249 símbolos con operación IEX reciente; [vigilante de captura](https://github.com/balempartev/fintual-precios/actions/runs/36008167854) con incidencia y [recuperación bot completada](https://github.com/balempartev/fintual-precios/actions/runs/36008187443). La prueba de apertura por `schedule` fue `FAILED`, con cero eventos genuinos, aunque los ciclos internos pasaron. Consulta [vigilancia viva](docs/vigilancia.json) y [estado vivo](docs/estado.json) para el último estado.
