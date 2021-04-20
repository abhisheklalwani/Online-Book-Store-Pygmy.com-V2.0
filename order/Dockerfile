FROM python:3.6.1-alpine
WORKDIR /app
ENV replica=http://localhost:8014
ENV catalog=http://localhost:8011
ENV host=0.0.0.0
ENV port=8013
ENV tag=order
COPY . /app
RUN pip3 install -r requirement.txt
CMD python3 order.py ${host} ${port} ${tag} ${replica} ${catalog}

