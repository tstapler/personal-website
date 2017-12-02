DEPLOY_DIR=deployment

PERSONAL_SITE=staplerstation
IOWA_STATE_SITE=iastate

DOCKER_TAG=tstapler/personal-website
DOCKER_RUN_COMMAND=docker run -it --rm --name personal-website -p 80:80 $(DOCKER_TAG):latest

serve:
	hugo serve --baseURL http://localhost

test-docker: build-personal
	$(DOCKER_RUN_COMMAND) -v "$(PWD)/deployment/dist/$(PERSONAL_SITE):/usr/share/nginx/html/"

test-personal-docker: build-personal-docker
	$(DOCKER_RUN_COMMAND)

build-personal-docker: build-personal
	docker build deployment -t $(DOCKER_TAG)

build-personal:
	hugo --baseURL http://tyler.staplerstation.com/ -d deployment/dist/$(PERSONAL_SITE)

deploy-personal: build-personal-docker
	docker push tstapler/personal-website:latest
	kubectl replace -f deployment/personal-site-deployment.yml

build-iastate:
	hugo --baseURL http://public.iastate.edu/~tstapler/ -d deployment/dist/$(IOWA_STATE_SITE)

upload-iastate: build-iastate
	sftp -r tstapler@sftp.iastate.edu < $(DEPLOY_DIR)/upload-iastate.batch
