FROM ubuntu:20.04

LABEL maintainer="Kesava Varma<kesava.varma@springml.com>"

LABEL maintainer="Rakesh <rakesh.madadi@springml.com>"

RUN apt-get update

RUN apt-get -y install python3.8 

RUN apt-get -y install python3-pip

# FROM python:3.8.10 

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8080

CMD [ "flask", "run", "--host=0.0.0.0" ,"--port=8080"]