USER=$1

if [ -z $USER ]; then
    echo "i got you bae";
    USER='poop';
fi

python manage_db.py -d &&
python manage_db.py -c &&
psql -d doko -f tests/fixtures/all-encompassing.sql && 
curl -is http://localhost:8888/debug/create/$USER

