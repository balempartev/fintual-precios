# Radar Fintual autónomo

Explora acciones y ETF estadounidenses en modo de **solo lectura**. No tiene funciones para operar, leer saldos, ni gestionar posiciones. Se ejecuta aproximadamente cada cinco minutos durante la sesión ordinaria de Nueva York; GitHub Actions puede retrasar o descartar ejecuciones.

## Qué puede comprobar

1. [Fintual informa más de 11.000 activos](https://ayuda.fintual.cl/es/articles/8592794-todas-las-acciones-etfs-disponibles-en-fintual) desde la ampliación de 2026. Su lista de enlaces individuales es una prueba pública para un subconjunto, pero ni esa lista ni un ticker listado demuestran que la cuenta de un usuario pueda operarlo. No se inicia sesión en Fintual.
2. Los archivos oficiales [Nasdaq Listed y Other Listed](https://www.nasdaqtrader.com/Trader.aspx?id=SymbolDirDefs) proporcionan candidatos de varias bolsas, con la marca ETF. Se descartan instrumentos que se puedan reconocer como derechos, warrants, unidades, preferentes, bonos y notas. Los restantes no son necesariamente todos instrumentos elegibles en Fintual. Se recorren todos los candidatos, sin filtrar industrias o sectores. Estas fuentes no incluyen una taxonomía sectorial completa: `sector_classification_complete=false` y los destacados aparecen como `UNCLASSIFIED` hasta contar con una fuente comprobable.
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

El cron usa `America/New_York`: 09:32, 09:37 ... 09:57; 10:02, 10:07 ... 15:57, de lunes a viernes. Antes de consultar, una solicitud **GET** al reloj de mercado de Alpaca confirma que la sesión está abierta, incluidos feriados y cierres anticipados. Si falla el reloj, no se consulta el mercado. `workflow_dispatch` permite una prueba manual incluso fuera de horario. `push` ejecuta pruebas locales sin explorar el mercado.

El escaneo divide el universo en lotes de 75 y refresca al final los candidatos destacados. El catálogo se comprueba una vez por fecha NY si las tres fuentes responden; los fallos se reintentan; si fallan las fuentes se conserva el último catálogo completo, o se recurre a la base histórica parcial de 2.090 símbolos, **marcando cobertura incompleta**. Si un lote falla se registra `batch_start` y `error`; una ejecución sin ningún snapshot devuelve error y no finge precios recientes. Los archivos de estado se actualizan al terminar una consulta; las edades se vuelven a calcular antes de publicar.

GitHub admite un intervalo mínimo de cinco minutos, pero [advierte retrasos, ejecuciones omitidas y desactivación tras 60 días sin actividad en repositorios públicos](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule). El flujo dura como máximo cinco minutos. No se envían alertas ni se gestionan las notificaciones horarias del usuario.

Secretos ya utilizados por el flujo: `ALPACA_API_KEY_ID` y `ALPACA_API_SECRET_KEY`. No se muestran ni se guardan sus valores. Los únicos destinos de las credenciales son las consultas GET de datos IEX y el reloj de mercado paper. El código usa biblioteca estándar Python 3.11; las pruebas no requieren red:

```bash
python -m unittest discover -s tests -v
```

## Opciones estudiadas

| Fuente / arquitectura | Alcance sin contratar | Limitación que importa | Decisión |
|---|---|---|---|
| [Alpaca Basic](https://docs.alpaca.markets/us/docs/about-market-data-api) + Actions | IEX en tiempo real, lotes de snapshots y 200 solicitudes/min | Cobertura y volumen solo IEX; prohíbe redistribución pública | Escaneo interno; precios e historial solo con repositorio privado |
| [Massive Basic](https://massive.com/pricing) | Todas las bolsas, fin del día, cinco solicitudes/min | Sin snapshots intradía gratis; servicio y cuenta adicionales | No contratar ni depender de ello |
| Nasdaq Screener web | Puede mostrar cambios amplios | Falló en las ejecuciones anteriores, a veces no aporta `asOf`; no es API pública confiable para este fin | Sustituido por directorios oficiales **solo para símbolos** |
| Nasdaq Symbol Directory + SEC EDGAR | Listados y documentos primarios públicos | No son cotizaciones ni verifican la cuenta Fintual | Catálogo, cobertura y vínculos a documentos |
| GitHub Actions + archivos versionados | Infraestructura ya existente, historial consultable | Cron aproximado y crecimiento del historial; repositorio público incompatible con publicar API prices | Se conserva, con barrera de privacidad automática |

**Verificación de producción:** [docs/VERIFICACION.md](docs/VERIFICACION.md) reúne las cuatro ejecuciones previas observables, sus fallos de periodicidad y los criterios pendientes para probar el nuevo radar. Los tests locales comprueban lógica y bloqueo de publicación; no sustituyen dos ejecuciones automáticas consecutivas.
