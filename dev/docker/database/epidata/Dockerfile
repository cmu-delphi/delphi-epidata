# start with a standard percona mysql image
FROM percona:ps-8

# percona exits with the mysql user but we need root for additional setup
USER root

# use delphi's timezome
RUN ln -s -f /usr/share/zoneinfo/America/New_York /etc/localtime

# specify a development-only password for the database user "root"
ENV MYSQL_ROOT_PASSWORD pass

# create the `epidata` database
ENV MYSQL_DATABASE epidata

# create the `user` account with a development-only password
ENV MYSQL_USER user
ENV MYSQL_PASSWORD pass

# provide DDL which will configure dev environment at container startup
COPY repos/delphi/delphi-epidata/dev/docker/database/epidata/_init.sql /docker-entrypoint-initdb.d/

# provide DDL which will create empty tables at container startup
COPY repos/delphi/delphi-epidata/src/ddl/*.sql /docker-entrypoint-initdb.d/

# provide additional configuration needed for percona
COPY repos/delphi/delphi-epidata/dev/docker/database/mysql.d/*.cnf /etc/my.cnf.d/

# grant access to SQL scripts
RUN chmod o+r /docker-entrypoint-initdb.d/*.sql

# restore mysql user for percona
USER mysql
