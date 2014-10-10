# About

This folder contains the requirements for the Ebola Reponse prototype, including requirements documents and database (SQL) fixtures which drive the survey form definitions.

## Requirements

* [HealthFacility_Questions_Guinea.xlsx](HealthFacility_Questions_Guinea.xlsx) 

   *source:* [Jilian A Sacks](jas2395@columbia.edu), Oct 7 2014

## Fixtures 

In the following commands, rather than `psql -U postgres` you can `sudo su postgres` to be able to use `psql` as the postgres user.

1. `$ psql -U postgres -d doko -f insert_fixture.sql` (Assuming system user postgres with access to the "doko" database -- these go in the connection string in [settings.py](https://github.com/SEL-Columbia/dokomoforms/blob/002dc3de3e285f13b407731418ee481ff89428f7/settings.py#L20-21))
2. `$ psql -U postgres -d doko`
3. `doko=# select survey_id from survey;`
4. Put this SURVEY_ID into local_settings.py

