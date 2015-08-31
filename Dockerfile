FROM python:3.4
WORKDIR /dokomo
ADD requirements.txt /dokomo/
RUN pip install -r requirements.txt
ADD . /dokomo
EXPOSE 8888
RUN head -c 24 /dev/urandom > cookie_secret
