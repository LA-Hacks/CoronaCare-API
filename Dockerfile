FROM python:3.7.2

ADD . /flask-deploy

WORKDIR /flask-deploy

RUN pip install -r requirements.txt

RUN pip install gunicorn[gevent]

EXPOSE 8080

ENV MONGO_URI=mongodb://db:27017/CoronaCare

CMD gunicorn --worker-class gevent --workers 8 --bind 0.0.0.0:8080 wsgi:app --max-requests 10000 --timeout 5 --keep-alive 5 --log-level info