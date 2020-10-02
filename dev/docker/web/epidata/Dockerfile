# start with the `delphi_web` image
FROM delphi_web

# deploy the Epidata API (see `delphi-epidata/deploy.json`)
COPY repos/delphi/delphi-epidata/src/server/*.html /var/www/html/epidata/
COPY repos/delphi/delphi-epidata/src/server/*.php /var/www/html/epidata/

# point to the development database (overwrites the production config)
COPY repos/delphi/delphi-epidata/dev/docker/web/epidata/assets/database_config.php /var/www/html/epidata/

RUN chmod o+r /var/www/html/epidata/*
