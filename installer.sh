#!/usr/bin/env sh
# Dokomo Forms installer for version 0.2.2
set -e

# Do you have docker installed?
if ! command -v docker > /dev/null; then
  printf "You need to install docker\n"
  exit 1
fi

# Do you have sed installed?
if ! command -v sed > /dev/null; then
  printf "You need to install sed\n"
  exit 1
fi

# Do you have openssl installed?
if ! command -v openssl > /dev/null; then
  printf "You need to install openssl\n"
  exit 1
fi

# Do you have curl installed?
if command -v curl > /dev/null; then
  CURL=curl
else
  CURL="docker run tutum/curl curl"
fi

# Do you have docker-compose installed?
if command -v docker-compose > /dev/null; then
  DOCKER_COMPOSE=docker-compose
else
  DOCKER_COMPOSE=./docker-compose
  if ! [ -f ./docker-compose ]; then
    printf "========================================\n"
    printf " Installing docker-compose in this      \n"
    printf " directory                              \n"
    printf "========================================\n"
    $CURL -o docker-compose -L https://github.com/docker/compose/releases/download/1.5.2/run.sh
    chmod +x docker-compose
    ./docker-compose -v
  fi
fi

# This installer needs root access for various reasons...
# Copy the logic from the letsencrypt-auto script
# https://github.com/letsencrypt/letsencrypt/blob/8c6e242b13ac818c0a94e3dceee81ab4b3816a12/letsencrypt-auto#L34-L68
if test "`id -u`" -ne "0" ; then
  if command -v sudo 1>/dev/null 2>&1; then
    SUDO=sudo
  else
    echo \"sudo\" is not available, will use \"su\" for installation steps...
    su_sudo() {
      args=""
      while [ $# -ne 0 ]; do
        args="$args'$(printf "%s" "$1" | sed -e "s/'/'\"'\"'/g")' "
        shift
      done
      su root -c "$args"
    }
    SUDO=su_sudo
  fi
else
  SUDO=
fi

# Ask for domain(s)
printf "========================================\n"
printf " Please enter your domain name(s) (space\n"
printf " separated)                             \n"
printf "                                        \n"
printf " Hint: for www include both             \n"
printf " >>> www.your.domain your.domain        \n"
printf "                                        \n"
printf " For a subdomain just give              \n"
printf " >>> subdomain.your.domain              \n"
printf "========================================\n"
printf "Domain(s):\n>>> "
read DOMAINS
LETSENCRYPT_DIR=$(echo $DOMAINS | cut -d' ' -f1)
DOMAIN_ARGS=$(echo $DOMAINS | sed -r s/\([^\ ]+\)/-d\ \\1/g)

# Run letsencrypt
printf "========================================\n"
printf " Installing SSL certificate. Make sure  \n"
printf " you have set up the DNS records for    \n"
printf " your domain to point to this machine.  \n"
printf "========================================\n"
$SUDO docker run -it --rm -p 443:443 -p 80:80 --name letsencrypt \
  -v "/etc/letsencrypt:/etc/letsencrypt:Z" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt:Z" \
  -v "/var/log:/var/log:Z" \
  quay.io/letsencrypt/letsencrypt:latest auth $DOMAIN_ARGS

# Run openssl dhparam
printf "========================================\n"
printf " Generating Diffie-Hellman parameters   \n"
printf " using OpenSSL (2048 bit prime)         \n"
printf "========================================\n"
$SUDO openssl dhparam -out /etc/letsencrypt/live/$LETSENCRYPT_DIR/dhparam.pem 2048

# Download the configuration files
printf "========================================\n"
printf " Downloading configuration files        \n"
printf "========================================\n"
$CURL -O https://raw.githubusercontent.com/SEL-Columbia/dokomoforms/v0.2.2/docker-compose.yml
$CURL -O https://raw.githubusercontent.com/SEL-Columbia/dokomoforms/v0.2.2/nginx.conf

# Edit the configuration files
printf "========================================\n"
printf " Generating final configuration         \n"
printf "========================================\n"

touch local_config.py

sed -i s/www.example.com/$LETSENCRYPT_DIR/g nginx.conf

printf "What is the name of your organization?  \n"
printf "This will be displayed as part of the   \n"
printf "title of the website.                   \n"
printf "Organization name:\n>>> "
read ORGANIZATION
printf "organization = '$ORGANIZATION'\n" >> local_config.py

printf "\n"
printf "Please enter an e-mail address for the  \n"
printf "administrator. This will be the only    \n"
printf "account that can log in at first.       \n"
printf "Administrator e-mail address:\n>>> "
read ADMIN_EMAIL
printf "admin_email = '$ADMIN_EMAIL'\n" >> local_config.py
DEFAULT_NAME=$(echo $ADMIN_EMAIL | cut -d'@' -f1)

printf "\n"
printf "Please enter a user name for the        \n"
printf "administrator. Leave this field blank to\n"
printf "use this user name:                     \n"
printf "$DEFAULT_NAME\n"
printf "Administrator user name:\n>>> "
read ADMIN_NAME
printf "admin_name = '${ADMIN_NAME:-$DEFAULT_NAME}'\n" >> local_config.py

# Let's Encrypt auto-renew (for now this is a cron job).
printf "========================================\n"
printf " Adding monthly cron job to renew SSL   \n"
printf " certificate.                           \n"
printf "========================================\n"
CRON_CMD="mkdir -p /tmp/letsencrypt-auto && docker run -it --rm --name letsencrypt -v /etc/letsencrypt:/etc/letsencrypt:Z -v /var/lib/letsencrypt:/var/lib/letsencrypt:Z -v /tmp/letsencrypt-auto:/tmp/letsencrypt-auto:Z -v /var/log/letsencrypt:/var/log/letsencrypt:Z quay.io/letsencrypt/letsencrypt --renew certonly -a webroot -w /tmp/letsencrypt-auto $DOMAIN_ARGS && docker restart $USER_nginx_1"
CRON_JOB="0 0 1 * * $CRON_CMD"
( crontab -l | fgrep -i -v "$CRON_CMD" ; echo "$CRON_JOB" ) | crontab -

# Bring up Dokomo Forms
printf "========================================\n"
printf " Starting Dokomo Forms.                 \n"
printf "                                        \n"
printf " You can view the status of the         \n"
printf " containers by running:                 \n"
printf " $DOCKER_COMPOSE ps\n"
printf "========================================\n"
if [ -f /etc/redhat-release ] ; then
  chcon -Rt svirt_sandbox_file_t .
fi
$DOCKER_COMPOSE up -d
