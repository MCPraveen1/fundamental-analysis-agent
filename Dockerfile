
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY agents/ ./agents/
COPY api/ ./api/
COPY config/ ./config/
COPY intelligence/ ./intelligence/
COPY reports/ ./reports/
COPY tools/ ./tools/

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
