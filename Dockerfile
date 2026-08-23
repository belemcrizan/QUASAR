FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip install --no-cache-dir .

RUN mkdir -p /data && chown -R 65532:65532 /data
USER 65532:65532

ENTRYPOINT ["quasar"]
CMD ["demo", "--domain", "all", "--points", "360", "--seed", "42", "--output-dir", "/data/demo"]

