FROM python:3.4
WORKDIR /dokomo
ADD requirements.txt /dokomo/
RUN pip install -r requirements.txt
ADD . /dokomo
COPY docker_settings.py /dokomo/dokomoforms/local_settings.py
EXPOSE 8888
CMD python manage_db.py --create
ENTRYPOINT python webapp.py
