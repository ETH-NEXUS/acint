# Action Interface (actint)

The Action Interface (actint) is a simple service that touches a file for the called action. 
For example if the action `.deploy` is called it touches a file into the `/do` folder inside 
the docker container.

## Environment

### `ACINT_ALLOWED_ACTIONS`

A comma separated list of actions to allow, default: .deploy

```bash
ACINT_ALLOWED_ACTIONS=.deploy
```

### `ACINT_PROXY_PATH`

The proxy path for the service, default: /

```bash
ACINT_PROXY_PATH=/
```

### `ACINT_TOKEN`

The security token to be used to authenticate

```bash
ACINT_TOKEN=keep_this_secret
```

### `ACINT_ENV`

The environment to use dev | prod, default: prod

```bash
ACINT_ENV=prod
```

## Integration into `smnrp`

```yaml
version: "3.9"
volumes:
  web_root:
  smnrp-data:

services:
  ws:
    image: ethnexus/smnrp:1.1.2
    ...
    depends_on:
      - acint
  acint:
    image: ethnexus/acint:main
    volumes:
      - ./.acint:/do
    # The following environment variables can be set:
    # ACINT_ALLOWED_ACTIONS=.deploy
    # ACINT_PROXY_PATH=/
    # ACINT_TOKEN=keep_this_secret
    env_file: .env
```

## Integration into github workflow

```yaml
...
jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    steps:
      - name: Trigger deployment
        id: deployTrigger
        uses: fjogeleit/http-request-action@v1
        with:
          url: ${{ secrets.DEPLOY_HOST }}
          method: "POST"
          customHeaders: '{"Content-Type": "application/json"}'
          data: '{ "action": "${{ secrets.ACINT_ACTION }}", "token": "${{ secrets.ACINT_TOKEN }}" }'
```