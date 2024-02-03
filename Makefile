DEPLOY_DIR=deployment

PERSONAL_SITE=staplerstation


DOCKER_TAG=tstapler/personal-website:latest
DOCKER_RUN_COMMAND=docker run -it --rm --name personal-website -p 80:80 $(DOCKER_TAG)

HUGO_URL=--baseURL $(SITE_URL)
HUGO_SERVE=hugo serve -D $(HUGO_URL)
HUGO_BUILD=hugo $(HUGO_URL)
HUGO_BUILD_SITE=$(HUGO_BUILD)


GULP_RUN=SITE_NAME=$(SITE_NAME) gulp
GULP_COMMANDS=$(GULP_RUN) meta-tags


BUILD_SITE= $(HUGO_BUILD_SITE)

serve: SITE_URL=http://localhost
serve:
	$(HUGO_SERVE)

serve-prod: SITE_URL=http://localhost
serve-prod:
	HUGO_ENV=production $(HUGO_SERVE)

test-docker: SITE_NAME=$(PERSONAL_SITE)
test-docker: DOCKER_TAG=nginx
test-docker: 
	$(DOCKER_RUN_COMMAND) -v "$(PWD)/$(DEPLOY_DIR)/dist/$(SITE_NAME):/usr/share/nginx/html/"



build-local: SITE_NAME=$(PERSONAL_SITE)
build-local: SITE_URL=http://127.0.0.1/
build-local: 
	$(BUILD_SITE)

build-local-docker: DOCKER_TAG=tstapler/personal-website:local
build-local-docker: 
	docker build --network host --build-arg SITE_URL=http://127.0.0.1/ . -t $(DOCKER_TAG)

test-local-docker: DOCKER_TAG=tstapler/personal-website:local
test-local-docker: build-local-docker
	$(DOCKER_RUN_COMMAND) 

build-personal: SITE_NAME=$(PERSONAL_SITE)
build-personal: SITE_URL=https://tyler.staplerstation.com/
build-personal: 
	$(BUILD_SITE)


DOCKER_TAG=ghcr.io/tstapler/personal-website:latest
build-personal-docker: 
	docker build --network host . -t $(DOCKER_TAG)

github-push: build-personal-docker 
	docker push $(DOCKER_TAG)

create-personal: 
	helm upgrade --install fettered-mind ./deployment/personal-website
