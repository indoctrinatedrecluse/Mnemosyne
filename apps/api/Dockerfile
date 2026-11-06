FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace/apps/api

COPY apps/api/pyproject.toml ./
COPY apps/api/mnemosyne_api ./mnemosyne_api
RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "mnemosyne_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
