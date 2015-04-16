# pulling both images
docker pull postgres:9.4.1
docker pull mdillon/postgis:9.4
docker build -t sel_columbia/dokomoforms .
# db: pssword, and create db doko
docker run -d -P --name dokomo_db -e POSTGRES_PASSWORD=password mdillon/postgis:9.4
echo "sleep now"
sleep 5
echo "wakie"
docker run --rm -i -t --link dokomo_db:postgres postgres sh -c 'exec psql -h "$POSTGRES_PORT_5432_TCP_ADDR" -p "$POSTGRES_PORT_5432_TCP_PORT" -U postgres'
#create database doko
docker run --rm --link dokomo_db:db sel_columbia/dokomoforms python manage_db.py --create
docker run -d -p 8888:8888 --name dokomo_webapp --link dokomo_db:db sel_columbia/dokomoforms python webapp.py

