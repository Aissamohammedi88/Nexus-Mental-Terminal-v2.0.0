FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY data/ ./data/

ENV NEXUS_DATA_PATH=/app/data
ENV NEXUS_LOG_LEVEL=INFO

ENTRYPOINT ["python", "-m", "src.cli.main"]
CMD ["--help"]
