FROM python:3.4
WORKDIR /dokomo
ADD requirements.txt /dokomo/
RUN pip install -r requirements.txt
RUN head -c 24 /dev/urandom > cookie_secret && sleep 1
EXPOSE 8888
