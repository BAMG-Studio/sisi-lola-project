FROM python:3.11-slim

WORKDIR /app

COPY sisi_lola_api/requirements.txt .
COPY sisi_lola_api/requirements_control_center.txt .

RUN pip install --no-cache-dir -r requirements.txt -r requirements_control_center.txt gunicorn

COPY sisi_lola_api/ .

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker"]
