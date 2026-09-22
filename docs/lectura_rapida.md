# Fintual × Nasdaq × Alpaca: actualización automática

**Extracción (UTC):** 2026-09-22T20:19:56Z
**Hora NY:** 2026-09-22T16:19:56-04:00
**Estado:** INCOMPLETE_NO_TRADE

**Alcance real de esta ejecución:**
- Base pública histórica Fintual (símbolos): 2090; NO prueba disponibilidad en la app.
- Filas Nasdaq descargadas: NO VERIFICABLE; frescura Nasdaq NO VERIFICABLE cuando asOf=null.
- Coincidencias Nasdaq-base Fintual: NO VERIFICABLE.
- Símbolos IEX solicitados: 15; con operación y cotización recientes: 0. IEX no es SIP consolidado.

| Ticker | Último IEX USD | Hora operación UTC | Edad seg. | Bid | Ask | Spread IEX | Dato reciente |
|---|---:|---|---:|---:|---:|---:|---|
| NVDA | 228.290 | 2026-09-22T20:10:31Z | 564.600 | 215.490 | 0.000 | — | NO |
| VKTX | 40.830 | 2026-09-22T19:59:57Z | 1198.600 | 39.050 | 43.110 | 9.883 | NO |
| GRAL | 108.515 | 2026-09-22T19:59:56Z | 1200.100 | 92.570 | 0.000 | — | NO |
| VICR | 267.870 | 2026-09-22T19:59:26Z | 1229.600 | 254.570 | 0.000 | — | NO |
| FLNA | 1.020 | 2026-09-22T20:04:35Z | 920.600 | 1.020 | 1.300 | 24.138 | NO |
| CMPX | 1.220 | 2026-09-22T19:59:57Z | 1199.000 | 1.060 | 1.440 | 30.400 | NO |
| GME | 24.035 | 2026-09-22T19:59:59Z | 1196.700 | 24.040 | 10000.000 | 199.041 | NO |
| GEV | 951.085 | 2026-09-22T19:59:48Z | 1207.700 | 907.850 | 991.200 | 8.778 | NO |
| AAPL | 339.850 | 2026-09-22T19:59:59Z | 1196.900 | 323.000 | 357.090 | 10.025 | NO |
| MSFT | 498.000 | 2026-09-22T19:59:58Z | 1198.000 | 471.870 | 522.630 | 10.208 | NO |
| AMZN | 254.985 | 2026-09-22T19:59:57Z | 1198.700 | 242.130 | 0.000 | — | NO |
| TSLA | 378.850 | 2026-09-22T19:59:59Z | 1196.500 | 360.050 | 398.030 | 10.020 | NO |
| AMD | 623.970 | 2026-09-22T19:59:59Z | 1196.300 | 588.080 | 0.000 | — | NO |
| AVGO | 364.490 | 2026-09-22T19:59:57Z | 1198.600 | 344.370 | 381.000 | 10.100 | NO |
| MU | 1092.880 | 2026-09-22T20:14:57Z | 298.900 | 1023.590 | 1149.870 | 11.620 | NO |

> **NO SON ÓRDENES DE COMPRA.** Solo una bolsa (IEX), no precios consolidados. No usar un spread IEX aislado como spread del mercado.
> Ninguna coincidencia pública demuestra que la acción esté habilitada en el contrato personal de Fintual.
> Comprobar en Fintual el precio real y las condiciones antes de operar.

**Advertencias:**
- Nasdaq no disponible: RuntimeError; se usó la lista prioritaria.
- Nasdaq asOf nulo/ausente: hora de precios masivos no verificable; sus cifras solo seleccionan símbolos.
