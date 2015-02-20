# add postgres packages
sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
apt-get install wget ca-certificates
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# update
apt-get update
apt-get upgrade

# install python 3
apt-get install -y python3
apt-get install -y python3-pip

# for convenience later, install vim
apt-get install -y vim

# setup locale
locale-gen

# install database deps
apt-get install -y postgresql postgresql-contrib postgis postgresql-server-dev-all

# install python deps
pip-3.2 install -r /vagrant/requirements.txt

# setup database and update postgres password
sudo su - postgres -c "createdb doko"
sudo su - postgres -c "psql -U postgres -d postgres -c \"alter user postgres with password 'password';\""
sudo su - postgres -c "python3 /vagrant/manage_db.py --create"

# link webroot
rm -rf /var/www
ln -fs /vagrant /var/www

# reset
