
test-docker:
	docker run --rm -v "$(PWD)/public:/usr/share/nginx/html/" --name personal-website -p 80:80 library/nginx:alpine

build-docker:
	docker build . -t tstapler/personal-website 

build-iastate:
	hugo --baseURL http://public.iastate.edu/~tstapler/ -d iastate

upload-iastate: build-iastate
	sftp -r tstapler@sftp.iastate.edu < upload-iastate.batch
