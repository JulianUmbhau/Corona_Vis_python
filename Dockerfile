FROM python:slim-buster

RUN apt-get update
RUN apt-get install nano

RUN mkdir wd
WORKDIR wd
COPY app/requirements.txt .
RUN pip3 install -r requirements.txt

COPY app/ .

CMD [ "python3", "app.py" ]