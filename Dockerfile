FROM python:3.4
WORKDIR /dokomo
ADD requirements.txt /dokomo/
RUN pip install -r requirements.txt
ADD . /dokomo
EXPOSE 8888
CMD python webapp.py
