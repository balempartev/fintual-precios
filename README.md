# Fintual × Nasdaq × Alpaca · actualización automática

Este repositorio contiene SOLO listas históricas de símbolos, código y precios bursátiles públicos. **Nunca publiques tus claves, contraseñas, nombres, saldo ni operaciones personales.**

## Configuración en GitHub

1. Crea un repositorio público vacío llamado `fintual-precios`.
2. Descomprime el ZIP y sube `actualizar_precios.py`, `universo_fintual_publico.csv`, `prioridad.txt`, `.gitignore` y `README.md` a la raíz del repositorio.
3. Sube `.github/workflows/precios.yml` respetando EXACTAMENTE esa ruta. En GitHub: `Add file` → `Create new file` y escribe `.github/workflows/precios.yml` como nombre, luego pega el contenido del archivo local. Si la carga de carpetas funciona desde el navegador, también puedes subir directamente toda la carpeta `.github`.
4. Dentro del repositorio: **Settings → Secrets and variables → Actions → New repository secret**. Crea ambos secretos `ALPACA_API_KEY_ID` y `ALPACA_API_SECRET_KEY`, pegando en GitHub las credenciales de *Paper Trading* que ya tienes en Colab. No compartas sus valores en ChatGPT ni en código.
5. Abre **Actions → Precios Fintual x Nasdaq x Alpaca → Run workflow** y espera a que la ejecución termine en verde. Si aparece error de permisos para publicar: **Settings → Actions → General → Workflow permissions → Read and write permissions**. Si aparece error de claves, comprueba nombres y secretos sin compartirlos.
6. Comprueba que existan `docs/precios.json` y `docs/lectura_rapida.md` con `generated_at_utc` reciente. La URL pública será `https://raw.githubusercontent.com/TU_USUARIO/fintual-precios/main/docs/precios.json` si creaste `main` como rama principal.
7. Comparte AQUÍ SOLAMENTE la dirección pública del repositorio. ChatGPT puede intentar leer `docs/lectura_rapida.md` y `docs/precios.json` durante cada informe horario y, una vez comprobado el acceso, actualizar el texto de la automatización que ya tienes. No hace falta compartir claves ni conectar ninguna cuenta personal a ChatGPT.

## Qué hace realmente

- Ejecuta cada 5 minutos durante el horario regular 09:30–15:59 de Nueva York (ajuste DST por `zoneinfo`). GitHub Actions puede retrasarse, no garantiza intervalos exactos; durante festivos sigue lanzándose pero no hay operaciones recientes y la frescura se marca como antigua.
- En cada ejecución intenta descargar el JSON masivo público de Nasdaq. **Si falla, aún consulta la lista prioritaria de acciones usando Alpaca.**
- Cruza los símbolos con una copia **histórica parcial** del listado público Fintual extraída del ZIP del 22 de septiembre. No demuestra cobertura de los >11.000 activos ni disponibilidad en tu contrato.
- Consulta a Alpaca SOLO endpoints de DATOS de mercado (`data.alpaca.markets`), con `feed=iex`. No hay órdenes de compra ni venta.
- Publica hora exacta de cada trade/quote, diferencia bid-ask IEX y antigüedad en segundos. Si una cotización carece de hora, NO la considera reciente.
- `OK_PARCIAL_RESEARCH_ONLY` **no significa que un ticker sea comprable**. Tampoco demuestra spread NBBO consolidado ni acceso real en tu app.
- Mecanismo de entrega a ChatGPT: archivo público que una revisión **puede consultar al ejecutarse**; no es un conector de transmisión continua, ni garantiza que cada ejecución de ChatGPT consiga leer GitHub. Un archivo antiguo se considera OBSOLETO.

Si estás usando un ordenador público, no pegues claves allí. Después de haber mostrado credenciales en capturas, usa las rotadas y nunca las reveles de nuevo.
