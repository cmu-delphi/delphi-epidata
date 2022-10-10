# `delphi_database_epidata`

This image extends a Percona database by:

- adding the `user` account
- adding the `epidata` &  other appropriate databases
- creating empty tables in those databases

To start a container from this image, run:

```bash
docker run --rm -p 13306:3306 \
  --network delphi-net --name delphi_database_epidata \
  delphi_database_epidata
```

For debugging purposes, you can interactively connect to the database inside
the container using a `mysql` client (either installed locally or supplied via
a docker image) like this:

```bash
mysql --user=user --password=pass --port 13306 --host 127.0.0.1 epidata
```

Note that using host `localhost` may fail on some platforms as mysql will
attempt, and fail, to use a Unix socket. Using `127.0.0.1`, which implies
TCP/IP, works instead.
