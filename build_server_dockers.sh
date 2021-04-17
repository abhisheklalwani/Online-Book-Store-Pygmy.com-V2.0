cd order/
docker build -t himgupta1996/pygmy:order .
docker push himgupta1996/pygmy:order
cd ../Catalog/
docker build -t himgupta1996/pygmy:catalog .
docker push himgupta1996/pygmy:catalog
cd ../frontend/
docker build -t himgupta1996/pygmy:frontend .
docker push himgupta1996/pygmy:frontend

