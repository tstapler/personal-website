DEPLOY_DIR=deployment

PERSONAL_SITE=staplerstation
IOWA_STATE_SITE=iastate

DOCKER_TAG=tstapler/personal-website
DOCKER_RUN_COMMAND=docker run -it --rm --name personal-website -p 80:80 $(DOCKER_TAG):latest

HUGO_URL=--baseURL $(SITE_URL)
HUGO_SERVE=hugo serve $(HUGO_URL)
HUGO_BUILD=hugo $(HUGO_URL)
HUGO_BUILD_SITE=$(HUGO_BUILD) $(HUGO_SITE_DIST) 
HUGO_SITE_DIST=-d $(DEPLOY_DIR)/pre_dist/$(SITE_NAME) 

UPDATE_DIST=rsync -ur $(DEPLOY_DIR)/pre_dist/$(SITE_NAME)/ $(DEPLOY_DIR)/dist/$(SITE_NAME)

GULP_RUN=SITE_NAME=$(SITE_NAME) gulp
GULP_COMMANDS=$(GULP_RUN) meta-tags


BUILD_SITE= $(HUGO_BUILD_SITE) && $(GULP_COMMANDS) && $(UPDATE_DIST)

serve: SITE_URL=http://localhost
serve:
	$(HUGO_SERVE)

test-docker: SITE_NAME=$(PERSONAL_SITE)
test-docker: DOCKER_TAG=nginx
test-docker: 
	$(DOCKER_RUN_COMMAND) -v "$(PWD)/$(DEPLOY_DIR)/dist/$(SITE_NAME):/usr/share/nginx/html/"

test-personal-docker: build-personal-docker
	$(DOCKER_RUN_COMMAND) 

build-personal-docker: build-personal
	docker build $(DEPLOY_DIR) -t $(DOCKER_TAG)

build-personal: SITE_NAME=$(PERSONAL_SITE)
build-personal: SITE_URL=https://tyler.staplerstation.com/
build-personal: 
	$(BUILD_SITE)

deploy-personal: build-personal-docker
	docker push tstapler/personal-website:latest
	helm upgrade --recreate-pods fettered-mind ./deployment/personal-website

create-personal: build-personal-docker
	helm install --name fettered-mind ./deployment/personal-website

build-iastate: SITE_NAME=$(IOWA_STATE_SITE) 
build-iastate: SITE_URL=http://public.iastate.edu/~tstapler/
build-iastate: 
	$(BUILD_SITE)

upload-iastate: build-iastate
	sftp -r tstapler@sftp.iastate.edu < $(DEPLOY_DIR)/upload-iastate.batch
