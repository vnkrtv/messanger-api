# Task consumer

- Gets tasks from the RabbitMQ exchange
- Process tasks:
    - makes FTS queries by search phrase among user's messages 
    - write search results to redis
