# Fintual × Nasdaq × Alpaca: actualización automática

**Extracción (UTC):** 2026-09-23T14:47:45Z
**Hora NY:** 2026-09-23T10:47:45-04:00
**Estado:** INCOMPLETE_NO_TRADE

**Alcance real de esta ejecución:**
- Base pública histórica Fintual (símbolos): 2090; NO prueba disponibilidad en la app.
- Filas Nasdaq descargadas: NO VERIFICABLE; frescura Nasdaq NO VERIFICABLE cuando asOf=null.
- Coincidencias Nasdaq-base Fintual: NO VERIFICABLE.
- Símbolos IEX solicitados: 15; con operación y cotización recientes: 0. IEX no es SIP consolidado.

| Ticker | Último IEX USD | Hora operación UTC | Edad seg. | Bid | Ask | Spread IEX | Dato reciente |
|---|---:|---|---:|---:|---:|---:|---|
| NVDA | 225.920 | 2026-09-23T14:48:32Z | -46.800 | 225.920 | 225.940 | 0.009 | NO |
| VKTX | 38.940 | 2026-09-23T14:48:35Z | -49.500 | 38.500 | 41.210 | 6.800 | NO |
| GRAL | 108.515 | 2026-09-22T19:59:56Z | 67669.400 | 92.570 | 0.000 | — | NO |
| VICR | 267.480 | 2026-09-23T14:48:19Z | -33.500 | 253.350 | 267.990 | 5.616 | NO |
| FLNA | 0.851 | 2026-09-23T14:39:04Z | 520.800 | 0.732 | 0.975 | 28.404 | NO |
| CMPX | 1.155 | 2026-09-23T14:48:03Z | -18.100 | 1.150 | 1.160 | 0.866 | NO |
| GME | 24.225 | 2026-09-23T14:48:33Z | -47.800 | 24.220 | 24.230 | 0.041 | NO |
| GEV | 944.640 | 2026-09-23T14:47:53Z | -8.100 | 895.660 | 997.500 | 10.759 | NO |
| AAPL | 337.840 | 2026-09-23T14:48:34Z | -49.400 | 337.840 | 337.900 | 0.018 | NO |
| MSFT | 499.415 | 2026-09-23T14:48:26Z | -40.600 | 499.240 | 499.540 | 0.060 | NO |
| AMZN | 249.635 | 2026-09-23T14:48:21Z | -36.200 | 249.540 | 249.590 | 0.020 | NO |
| TSLA | 379.330 | 2026-09-23T14:48:31Z | -46.400 | 379.090 | 385.750 | 1.742 | NO |
| AMD | 610.650 | 2026-09-23T14:48:27Z | -42.100 | 610.670 | 613.130 | 0.402 | NO |
| AVGO | 355.260 | 2026-09-23T14:48:34Z | -48.500 | 354.920 | 355.540 | 0.175 | NO |
| MU | 1075.740 | 2026-09-23T14:48:29Z | -44.200 | 1071.000 | 1078.200 | 0.670 | NO |

> **NO SON ÓRDENES DE COMPRA.** Solo una bolsa (IEX), no precios consolidados. No usar un spread IEX aislado como spread del mercado.
> Ninguna coincidencia pública demuestra que la acción esté habilitada en el contrato personal de Fintual.
> Comprobar en Fintual el precio real y las condiciones antes de operar.

**Advertencias:**
- Nasdaq no disponible: RuntimeError; se usó la lista prioritaria.
- Nasdaq asOf nulo/ausente: hora de precios masivos no verificable; sus cifras solo seleccionan símbolos.
