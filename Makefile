.PHONY: all
all: format check test

.PHONY: test
test:
	rye run pytest

.PHONY: format
format:
	rye run autoflake .
	rye run isort .
	rye run black .

.PHONY: check
check:
	rye run flake8 ./src
	rye run vulture

.PHONY: update
update:
	rye sync --update-all

.PHONY: docker
docker:
	-docker stop container-pss-fleet-data
	docker rm -f container-pss-fleet-data
	docker image rm -f image-pss-fleet-data:latest
	docker build -t image-pss-fleet-data .
	docker run -d --name container-pss-fleet-data image-pss-fleet-data:latest