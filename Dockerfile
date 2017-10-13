FROM python:3.4
WORKDIR /dokomo
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get update && apt-get install npm nodejs postgresql-client -y
ADD package.json /tmp/package.json
RUN cd /tmp && npm install && npm install lodash --save-dev
RUN cp -a /tmp/node_modules /dokomo/
ADD . /dokomo/
RUN pip install -r requirements.txt
RUN nodejs node_modules/gulp/bin/gulp.js build
RUN mkdir -p /var/www/static/dist
RUN cp -r /dokomo/dokomoforms/static/dist /var/www/static
RUN cp /dokomo/dokomoforms/static/robots.txt /var/www/static/robots.txt
RUN cp /dokomo/dokomoforms/static/manifest.json /var/www/static/manifest.json
RUN cp /dokomo/dokomoforms/static/src/common/img/favicon.png /var/www/static/favicon.png
EXPOSE 8888
