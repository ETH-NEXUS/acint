# Action Interface (actint)

The Action Interface (actint) is a simple web service that touches a file for the called action. 
For example if the action `.deploy` is called it touches a file into the `/do` folder inside 
the docker container. You can configure a volume to mount the `/do` folder to and use this 
as a kind of a postbox to see what action to was triggered using the web service.

It is built with the intention, that it can be used in Git workflows to trigger an action on
a deployment host.

## Environment

The following environment variable can be used ton configure `acint`.

### `ACINT_ALLOWED_ACTIONS`

A comma separated list of actions to allow, default: `.deploy`

```bash
ACINT_ALLOWED_ACTIONS=.deploy
```

### `ACINT_PROXY_PATH`

The proxy path for the service, default: `/`

```bash
ACINT_PROXY_PATH=/
```

### `ACINT_TOKEN`

The security token to be used to authenticate, default: a random `uuid4`

```bash
ACINT_TOKEN=keep_this_secret
```

### `ACINT_ENV`

The environment to use: `dev` | `prod`, default: `prod`

```bash
ACINT_ENV=prod
```

## Integration into `smnrp`

The service is built to be easily integrated into [`smnrp`](https://hub.docker.com/repository/docker/ethnexus/smnrp). 
The following example `docker-compose` and `.env` shows how to run `acint` beside `smnrp`.

### `docker-compose.yml`

```yaml
version: "3.9"
volumes:
  web_root:
  smnrp-data:

services:
  ws:
    image: ethnexus/smnrp
    ...
    depends_on:
      - acint
  acint:
    image: ethnexus/acint
    volumes:
      - ./.acint:/do
    env_file: .env
```

### `.env`

```bash
...
SMNRP_UPSTREAMS=acint!acint:80
SMNRP_UPSTREAM_PROTOCOL=http
SMNRP_LOCATIONS=/acint/!http://acint/
...
ACINT_ALLOWED_ACTIONS=.deploy
ACINT_PROXY_PATH=/
ACINT_TOKEN=keep_this_secret
...
```

## Integration into github workflow

The `acint` web service can be triggered from a git workflow using the `fjogeleit/http-request-action@v1` action.
Here is an example workflow that triggers on any new tag (after `git tag -a v1.0.0`, `git push --tags`): 

### `.github/workflows/deploy.yml`

```yaml
name: Deploy Application
on:
  push:
    tags:
      - "*"
jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest
    steps:
      - name: Trigger deployment
        id: deployTrigger
        uses: fjogeleit/http-request-action@v1
        with:
          url: ${{ secrets.ACINT_URL }}
          method: "POST"
          customHeaders: '{"Content-Type": "application/json"}'
          data: '{ "action": "${{ secrets.ACINT_ACTION }}", "token": "${{ secrets.ACINT_TOKEN }}" }'
```

Please make sure you have set up the following secrets in the git repository:

- `ACINT_URL`: The url to the acint service (e.g. `https://domain.com/acint/`)
- `ACINT_ACTION`: The action to trigger (must be listed in `ACINT_ALLOWED_ACTIONS`)
- `ACINT_TOKEN`: The token used to authenticate the request (must be identical to `ACINT_TOKEN`)

## Example script

The following script can be added to a crontab to be run every minute. It will run the redeploy command `make redeploy` if 
the `DEPLOY_TRIGGER` file exists. The same principle can be adapted for any action you want to trigger from "outside".

### `redeployIfNeeded.sh`

```bash
#!/usr/bin/env bash

PROJECT_DIR="/path/to/project"
DEPLOY_TRIGGER="${PROJECT_DIR}/.acint/.deploy"

if [ -f ${DEPLOY_TRIGGER} ]; then
    rm -f ${DEPLOY_TRIGGER}
    cd ${PROJECT_DIR}
    make redeploy
fi
```

### Crontab entry

```crontab
* * * * * /opt/projects/wisedashboard/scripts/redeployIfNeeded.sh
```