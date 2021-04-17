FROM ubuntu:16.04
RUN apt update && apt install python -y
RUN apt install python-pip -y
COPY ./requirement.txt /app/requirement.txt
WORKDIR /app
RUN pip install -r requirement.txt
COPY . /app
CMD python order.py

