# start with the `delphi_database` image
FROM delphi_database

# create the `epidata` database
ENV MYSQL_DATABASE epidata

# create the `epi` user account with a development-only password
ENV MYSQL_USER user
ENV MYSQL_PASSWORD pass

# provide DDL which will create empty tables at container startup
COPY repos/delphi/delphi-epidata/src/ddl/*.sql /docker-entrypoint-initdb.d/

# grant access to SQL scripts
RUN chmod o+r /docker-entrypoint-initdb.d/*.sql
