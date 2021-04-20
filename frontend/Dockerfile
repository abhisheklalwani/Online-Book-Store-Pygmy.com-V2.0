FROM python:3.6.1-alpine
WORKDIR /app
ENV host=0.0.0.0
ENV port=8010
ENV catalogA=http://0.0.0.0:8011
ENV catalogB=http://0.0.0.0:8012
ENV orderA=http://0.0.0.0:8013
ENV orderB=http://0.0.0.0:8014
COPY . /app
RUN pip3 install -r requirement.txt
CMD python3 frontend.py ${host} ${port} ${catalogA} ${catalogB} ${orderA} ${orderB} 

