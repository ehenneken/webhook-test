# Webhook test

## Docker

### Build image

```
docker build -t webhooktest:latest .
```

### Run container

```
mkdir $HOME/tmp/
docker run -d -p 9000:9000 -v $HOME/tmp:/tmp --name webhooktest webhooktest
```

