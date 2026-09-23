# Fintual × Nasdaq × Alpaca: actualización automática

**Extracción (UTC):** 2026-09-23T15:21:37Z
**Hora NY:** 2026-09-23T11:21:37-04:00
**Estado:** OK_PARCIAL_RESEARCH_ONLY

**Alcance real de esta ejecución:**
- Base pública histórica Fintual (símbolos): 2090; NO prueba disponibilidad en la app.
- Filas Nasdaq descargadas: NO VERIFICABLE; frescura Nasdaq NO VERIFICABLE cuando asOf=null.
- Coincidencias Nasdaq-base Fintual: NO VERIFICABLE.
- Símbolos IEX solicitados: 15; con operación y cotización recientes: 12. IEX no es SIP consolidado.

| Ticker | Último IEX USD | Hora operación UTC | Edad seg. | Bid | Ask | Spread IEX | Dato reciente |
|---|---:|---|---:|---:|---:|---:|---|
| NVDA | 225.610 | 2026-09-23T15:22:22Z | 4.400 | 225.620 | 225.640 | 0.009 | SÍ |
| VKTX | 41.910 | 2026-09-23T15:21:56Z | 30.300 | 39.900 | 42.250 | 5.721 | SÍ |
| GRAL | 108.515 | 2026-09-22T19:59:56Z | 69751.100 | 92.570 | 0.000 | — | NO |
| VICR | 275.225 | 2026-09-23T15:16:17Z | 369.900 | 275.010 | 279.120 | 1.483 | NO |
| FLNA | 0.875 | 2026-09-23T15:11:45Z | 642.100 | 0.750 | 0.992 | 27.764 | NO |
| CMPX | 1.175 | 2026-09-23T15:21:56Z | 31.100 | 1.170 | 1.180 | 0.851 | SÍ |
| GME | 24.445 | 2026-09-23T15:22:15Z | 11.400 | 24.430 | 24.450 | 0.082 | SÍ |
| GEV | 951.965 | 2026-09-23T15:22:13Z | 13.800 | 895.660 | 997.500 | 10.759 | SÍ |
| AAPL | 337.570 | 2026-09-23T15:22:19Z | 8.200 | 337.370 | 337.570 | 0.059 | SÍ |
| MSFT | 498.025 | 2026-09-23T15:22:26Z | 0.900 | 497.800 | 498.320 | 0.104 | SÍ |
| AMZN | 250.640 | 2026-09-23T15:22:14Z | 12.600 | 250.540 | 250.660 | 0.048 | SÍ |
| TSLA | 381.150 | 2026-09-23T15:22:18Z | 9.200 | 380.730 | 382.640 | 0.500 | SÍ |
| AMD | 615.725 | 2026-09-23T15:22:11Z | 15.800 | 615.630 | 619.050 | 0.554 | SÍ |
| AVGO | 357.150 | 2026-09-23T15:22:26Z | 0.800 | 354.380 | 358.790 | 1.237 | SÍ |
| MU | 1082.235 | 2026-09-23T15:22:21Z | 5.400 | 1072.000 | 1084.300 | 1.141 | SÍ |

> **NO SON ÓRDENES DE COMPRA.** Solo una bolsa (IEX), no precios consolidados. No usar un spread IEX aislado como spread del mercado.
> Ninguna coincidencia pública demuestra que la acción esté habilitada en el contrato personal de Fintual.
> Comprobar en Fintual el precio real y las condiciones antes de operar.

**Advertencias:**
- Nasdaq no disponible: RuntimeError; se usó la lista prioritaria.
- Nasdaq asOf nulo/ausente: hora de precios masivos no verificable; sus cifras solo seleccionan símbolos.
