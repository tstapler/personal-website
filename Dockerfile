FROM klakegg/hugo:0.111.3-ext
# Install latest chrome dev package and fonts to support major charsets (Chinese, Japanese, Arabic, Hebrew, Thai and a few others)
# Note: this installs the necessary libs to make the bundled version of Chromium that Puppeteer
# installs, work.
RUN apt-get update \
    && apt-get install -y wget gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf libxss1 libx11-xcb-dev libxtst-dev \
      --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build/
# Install puppeteer so it's available in the container.
RUN npm i puppeteer

ARG SITE_URL=https://tyler.staplerstation.com/
ARG HUGO_BUILD_ENV=production
RUN npm install --global critical gulp fancy-log --unsafe-perm=true --allow-root
COPY package.json package.json
RUN npm install
COPY . ./
RUN HUGO_ENV=$HUGO_BUILD_ENV hugo --baseURL $SITE_URL
RUN gulp critical
RUN gulp compress

FROM library/nginx:latest

COPY deployment/personal-website/files/default.conf /etc/nginx/conf.d/default.conf
COPY deployment/personal-website/files/nginx.conf /etc/nginx/nginx.conf
COPY --from=0 /build/public /usr/share/nginx/html
