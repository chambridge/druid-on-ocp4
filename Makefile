OS := $(shell uname)
ifeq ($(OS),Darwin)
	PREFIX	=
else
	PREFIX	= sudo
endif


help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "--- Commands using an OpenShift Cluster ---"
	@echo "  setup-pull-secret                  setup the pull secret for the Red Hat registry (assumes OCP4/CRC)"
	@echo ""
	@echo "--- Commands using Docker Compose ---"
	@echo "  docker-up                          run docker-compose up -d"
	@echo "  docker-down                        shut down all containers"
	@echo "  docker-logs                        connect to console logs for all services"

setup-pull-secret:
	oc get secret pull-secret --namespace=openshift-config --export -o yaml | oc apply -f -

docker-down:
	docker-compose -f ../druid/distribution/docker/docker-compose.yml down

docker-logs:
	docker-compose logs -f

docker-druid-setup:
	@cp -fr deploy/ testing/
	@sed -i "" 's/aws_access/'"${AWS_ACCESS_KEY_ID}"'/g' testing/environment
	@sed -i "" 's/aws_secret/'"${AWS_SECRET_ACCESS_KEY}"'/g' testing/environment
	@sed -i "" 's/aws_region/'"${AWS_REGION}"'/g' testing/environment
	@cp -fr testing/environment ../druid/distribution/docker

docker-up: docker-druid-setup
	docker-compose -f ../druid/distribution/docker/docker-compose.yml up -d
