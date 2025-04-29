.PHONY: build
build:
	docker build -t fastapi-example .

.PHONY: start
start:
	docker run --detach --name example --publish 80:80 fastapi-example

.PHONY: stop
stop:
	docker container stop example || echo "Proceeding"
	echo "y" | docker container prune

.PHONY: clean
clean: stop
	docker image rm fastapi-example || echo "Proceeding"
