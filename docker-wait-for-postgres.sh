#!/bin/sh
until psql --host=$1 --username=postgres -w &>/dev/null
do
  echo "Waiting for PostgreSQL..."
  sleep 1
done
