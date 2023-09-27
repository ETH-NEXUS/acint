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

The proxy path for the service, default: /acint

```bash
ACINT_PROXY_PATH=/acint
```