FROM python:3.4
WORKDIR /dokomo
RUN apt-get update && apt-get install npm nodejs -y
ADD package.json /tmp/package.json
RUN cd /tmp && npm install && npm install lodash --save-dev
RUN cp -a /tmp/node_modules /dokomo/
ADD . /dokomo/
RUN pip install -r requirements.txt
RUN nodejs node_modules/gulp/bin/gulp.js build
EXPOSE 8888
