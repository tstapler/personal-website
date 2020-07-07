FROM 0.73.0-ubuntu-onbuild
ARG SITE_URL=https://tyler.staplerstation.com/
ARG HUGO_ENV=production
WORKDIR /build/
COPY . ./
RUN hugo --baseURL $SITE_URL

FROM library/nginx:latest

COPY deployment/default.conf /etc/nginx/conf.d/default.conf
COPY deployment/nginx.conf /etc/nginx/nginx.conf
COPY --from=0 /build/public /usr/share/nginx/html
