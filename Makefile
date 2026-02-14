
run: docker-compose.yml Dockerfile
	docker-compose up --build

del-run:
	docker-compose down -v && make run
