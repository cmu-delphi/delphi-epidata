# `delphi_web_epidata`

This image starts with Delphi's web server and adds the sources necessary for
hosting the Epidata API.

This image includes the file
[`database_config.php`](assets/database_config.php), which points to a local
container running the
[`delphi_database_epidata` image](../../database/epidata/README.md).

To start a container from this image, run:

```bash
docker run --rm -p 10080:80 \
  --network delphi-net --name delphi_web_epidata \
  delphi_web_epidata
```

You should be able to call the API by setting your base URL to
`http://localhost:10080/epidata/api.php`. To verify that the container is alive
and serving, visit in a web browser (or `curl`)
http://localhost:10080/epidata/.
