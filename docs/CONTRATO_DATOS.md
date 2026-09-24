# Contrato de datos y privacidad

| Ruta / fuente | Clase | Se permite publicar aquí | Qué NO demuestra |
|---|---|---|---|
| `docs/catalogo.json` | Directorios públicos y enlaces Fintual | Ticker, bolsa, tipo, enlace, fecha y advertencias | Compra habilitada en la cuenta Fintual; catálogo exhaustivo oficial |
| `docs/estado.json`, `docs/audit/*.jsonl` | Telemetría operativa | Conteos agregados, errores, identificador y hora del job | Precio actual de un símbolo o cobertura SIP |
| `docs/catalizadores.json` | URL/título/hora de FDA/Fed; SEC si disponible | Enlaces a documentos primarios y su fecha, sin extracción masiva ni precio | Causalidad del precio, noticias empresariales exhaustivas |
| `docs/sectores.json` | Etiquetas de fichas públicas de Fintual por símbolo | Etiquetas breves, fuente, fecha, número clasificado y errores de consulta | Taxonomía GICS, sector único, etiqueta para todos los símbolos o negociabilidad personal |
| `docs/precios.json` en repositorio **público** | Barrera de licencia | Solo estado `PUBLIC_NO_MARKET_DATA` | Historial de cotizaciones accesible a Tasks |
| `history/*.jsonl` en repo **privado**, si algún día se valida el acceso | Datos Alpaca IEX | Solo acceso autorizado y retención pactada; nunca copiar al repo público | Redistribución libre o precios consolidados |
| `confirmations` en Sites privado | Saldo, posiciones, órdenes, fills | Nunca en este repo; leer `is_test=0`, fecha y base completa validada | Fills inferidos de una recomendación; una fila de prueba como cartera |

IEX es una bolsa. Sus operaciones, barras y cotizaciones llevan hora propia; el resultado del job no hace que todos los símbolos sean recientes. El indicador `volume_activity_proxy_iex` compara volumen IEX acumulado con el día anterior y tiempo transcurrido; no es RVOL de 20 días ni volumen consolidado. Las etiquetas Fintual son múltiples por empresa y progresivas; los once ETF sectoriales son referencias separadas. Nunca publicar ranking, porcentajes, spreads ni volumen por símbolo derivados de la API en un repositorio público.

Alpaca advierte que su API no confiere redistribución de datos: [política](https://alpaca.markets/support/redistribute-alpaca-api). El historial antiguo de Git del repositorio puede contener cotizaciones publicadas antes de esta barrera; eliminar archivos actuales no elimina los commits históricos. Una limpieza histórica y cambio de visibilidad requieren una transición aparte y comprobación de consumidores. Este documento no afirma que ese riesgo histórico esté saneado.
