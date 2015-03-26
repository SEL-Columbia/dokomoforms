# add postgres packages
sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
apt-get install wget ca-certificates
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# update
apt-get update
apt-get upgrade

# compilers and whatnot
apt-get install -y build-essential
apt-get install -y git

# install ssh, required by pip
apt-get install -y libssl-dev openssl

# install python
wget http://www.python.org/ftp/python/3.4.1/Python-3.4.1.tar.xz
tar xJf ./Python-3.4.1.tar.xz
cd Python-3.4.1
./configure --with-ensurepip=install
make
make install

# make python3 the default python
ln -s /usr/local/bin/python3 /usr/local/bin/python

# apt-get install -y python3-pip

# for convenience later, install vim
apt-get install -y vim

# setup locale
locale-gen

# install database deps
apt-get install -y postgresql postgresql-contrib postgis postgresql-server-dev-all

# chown shared folder
sudo chown vagrant:www-data /vagrant

# install python deps
# NOTE: this uses pip-3.2, which installed by default
pip3 install -r /vagrant/requirements.txt

# setup database and update postgres password
sudo su - postgres -c "createdb doko"
sudo su - postgres -c "psql -U postgres -d postgres -c \"alter user postgres with password 'password';\""
sudo su - postgres -c "python /vagrant/manage_db.py --create"

# add nginx
sudo apt-get install nginx

# link webroot
rm -rf /var/www
ln -fs /vagrant /var/www

# reset
