VERSION 0.7

args:
    ARG SITE_NAME = "staplerstation"
    ARG DEPLOY_DIR = "deployment"
    ARG DOCKER_TAG = "ghcr.io/tstapler/personal-website:latest"
    ARG HUGO_URL = "https://tyler.staplerstation.com/"

base-build:
    FROM earthly/hugo:0.101.0
    WORKDIR /project
    COPY . .
    RUN npm install

serve:
    FROM +base-build
    ARG HUGO_URL
    RUN hugo serve -D --base-buildURL "$HUGO_URL" --bind 0.0.0.0

build-local:
    FROM +base-build
    ARG HUGO_URL = "http://127.0.0.1/"
    RUN hugo --base-buildURL "$HUGO_URL"
    SAVE ARTIFACT public /project/public AS LOCAL ./public

docker:
    FROM +base-build
    COPY deployment/personal-website/files/nginx.conf /etc/nginx/conf.d/default.conf
    RUN hugo --base-buildURL "$HUGO_URL"
    SAVE IMAGE --push "$DOCKER_TAG"

#deploy:
#    FROM earthly/helm:3.12.3
#    COPY deployment/personal-website/ ./deployment/personal-website/
#    WITH DOCKER \
#        --compose docker-compose.yml \
#        --load $DOCKER_TAG
#    RUN helm upgrade --install fettered-mind ./deployment/personal-website

test-local:
    FROM nginx:alpine
    COPY deployment/personal-website/files/nginx.conf /etc/nginx/conf.d/default.conf
    COPY +build-local/public /usr/share/nginx/html
    EXPOSE 80
    ENTRYPOINT ["nginx", "-g", "daemon off;"]
