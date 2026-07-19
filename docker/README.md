# RetailPulse — Docker Deployment

## Build & run locally

```bash
# from the repo root
docker build -f docker/Dockerfile -t retailpulse-dashboard:latest .
docker run -p 8501:8501 retailpulse-dashboard:latest
```

Or with docker-compose (also brings up an MLflow UI on port 5000):

```bash
cd docker
docker compose up --build
```

Dashboard: http://localhost:8501
MLflow UI: http://localhost:5000

## Design notes

- **Multi-stage build**: a `builder` stage installs dependencies into a virtualenv;
  the `runtime` stage copies only that venv plus the app code — no compilers or
  build tools ship in the final image.
- **Non-root user**: the container runs as an unprivileged `retailpulse` user.
- **Minimal dependency set**: `requirements-dashboard.txt` contains only what the
  dashboard code actually imports (streamlit, pandas, numpy, plotly, reportlab) —
  verified by statically parsing every `.py` file under `dashboard/` and diffing
  the import list against the requirements file. The full training/notebook stack
  (Prophet, PyTorch, XGBoost, MLflow, Evidently, Optuna, SHAP) lives in the
  separate `requirements-pipeline.txt`, since the dashboard only reads
  already-computed CSV/JSON outputs and never loads those heavier libraries at
  runtime.
- **Healthcheck**: hits Streamlit's built-in `/_stcore/health` endpoint.

## Validation performed in this environment

Docker isn't available in the sandbox this project was built in, so the
Dockerfile and compose file could not be build-tested with a live daemon here.
What **was** validated:
- `docker-compose.yml` parses as valid YAML
- Every third-party import across all dashboard `.py` files was extracted via
  Python's `ast` module and cross-checked against `requirements-dashboard.txt`
  (all present, and the file was trimmed to remove unused entries)
- The Dockerfile's `COPY` paths were checked against the actual files
  `dashboard/utils/data_loader.py` reads, to confirm every file the app needs
  at runtime is included in the image

Before deploying, run `docker build` locally once to confirm the image builds
in your actual environment.
