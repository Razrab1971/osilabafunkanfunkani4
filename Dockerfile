# -- Сборщик --
FROM debian:bookworm-slim AS builder

RUN apt-get update && apt-get install -y \
   g++ \
   && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY dop_application/. .

RUN g++ shifr.cpp -o shifr



# -- Основная система --
FROM python:3.12-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
	libpq-dev \
	&& rm -rf var/lib/apt/lists/*


COPY telegram_bot/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY --from=builder build/shifr .
COPY telegram_bot/. .


RUN \
	chown -R 1000:1000 /app && \
	chmod -R 755 /app

RUN useradd -m -u 1000 appuser
USER appuser

RUN chmod +x start.sh

#EXPOSE 8000


CMD ["./start.sh"]


