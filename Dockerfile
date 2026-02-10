FROM python:3.12-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
	libpq-dev \
	&& rm -rf var/lib/apt/lists/*


COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt


COPY . .


RUN \
	chown -R 1000:1000 /app && \
	chmod -R 755 /app

RUN useradd -m -u 1000 appuser
USER appuser

RUN chmod +x start.sh

#EXPOSE 8000


CMD ["./start.sh"]


