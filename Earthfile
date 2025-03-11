VERSION 0.7

args:
    ARG SITE_NAME = "staplerstation"
    ARG DEPLOY_DIR = "deployment"
    ARG DOCKER_TAG = "mirror.gcr.io/YOUR_PROJECT/YOUR_REPO/personal-website:latest"
    ARG HUGO_URL = "https://tyler.staplerstation.com/"
    ARG EARTHLY_PARALLELISM = "3"  # Reduce default parallelism

base-build:
    FROM mirror.gcr.io/hugomods/hugo:exts
    WORKDIR /project
    # Separate dependencies to optimize caching
    COPY package.json package-lock.json ./
    RUN npm install --omit=dev
    # Copy remaining files after dependencies
    COPY . .

serve:
    FROM +base-build
    ARG HUGO_URL
    RUN hugo serve -D --base-buildURL "$HUGO_URL" --bind 0.0.0.0 --renderToMemory

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
    FROM mirror.gcr.io/library/nginx:alpine
    COPY deployment/personal-website/files/nginx.conf /etc/nginx/conf.d/default.conf
    COPY +build-local/public /usr/share/nginx/html
    EXPOSE 80
    ENTRYPOINT ["nginx", "-g", "daemon off;"]
