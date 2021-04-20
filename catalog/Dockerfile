FROM python:3.6.1-alpine
WORKDIR /app
ENV host=0.0.0.0
ENV port=8013
ENV replica=http://localhost:8014
ENV tag=catalog
COPY . /app
RUN pip3 install -r requirement.txt
CMD python3 catalog.py ${host} ${port} ${tag} ${replica}

