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
    
    # Install project dependencies
    COPY package.json ./

    # Copy source files
    COPY . .

serve:
    FROM +base-build
    ARG HUGO_URL
    RUN hugo serve --buildDrafts --baseURL "$HUGO_URL" --bind 0.0.0.0 --renderToMemory

build-local:
    FROM +base-build
    ARG HUGO_URL = "http://127.0.0.1/"
    RUN hugo --base-buildURL "$HUGO_URL"
    SAVE ARTIFACT public /project/public AS LOCAL ./public

docker:
    FROM +base-build
    # Copy nginx configurations to correct locations
    COPY deployment/personal-website/files/default.conf /etc/nginx/conf.d/default.conf
    COPY deployment/personal-website/files/nginx.conf /etc/nginx/nginx.conf
    # Build with production environment
    RUN HUGO_ENV=production hugo --baseURL "$HUGO_URL"
    
    # Run post-processing tasks
    RUN gulp critical
    RUN gulp compress
    
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
