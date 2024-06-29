FROM redis

ENV REDIS_PASSWORD=$REDIS_PASSWORD

CMD ["sh", "-c", "exec redis-server --requirepass \"$REDIS_PASSWORD\""]