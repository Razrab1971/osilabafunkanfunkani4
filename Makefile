
run: docker-compose.yml Dockerfile
	docker-compose -f ./docker-compose.yml up --build

del-run:
	docker-compose down -v && make run
