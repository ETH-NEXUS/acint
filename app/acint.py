#!/usr/bin/env python3

import os
import cherrypy
from uuid import uuid4


DO_PATH = os.path.join(os.path.sep, "do")
os.makedirs(DO_PATH, exist_ok=True)

allowed_actions_string = os.environ.get("ACINT_ALLOWED_ACTIONS", "").strip()
if len(allowed_actions_string) == 0:
    allowed_actions = [".deploy"]
else:
    allowed_actions = os.environ.get("ACINT_ALLOWED_ACTIONS", ".deploy").split(",")
proxy_path = os.environ.get("ACINT_PROXY_PATH", None) or "/"
secure_token = os.environ.get("ACINT_TOKEN", None) or uuid4().hex
environment = os.environ.get("ACINT_ENV", None) or "prod"

env_config = {
    "environments": {
        "dev": {
            "tools.log_headers.on": True,
        },
        "prod": {
            "engine.autoreload.on": False,
            "checker.on": False,
            "tools.log_headers.on": False,
            "request.show_tracebacks": False,
            "request.show_mismatched_params": False,
            "log.screen": False,
        },
    },
}


def handle_an_exception():
    cherrypy.response.status = 500
    cherrypy.response.headers["content-type"] = "text/plain;charset=UTF-8"
    cherrypy.response.body = b"Internal Server Error"


def handle_default(status=None, message=None, version=None, traceback=None):
    cherrypy.response.headers["content-type"] = "text/plain;charset=UTF-8"
    return f"{status}".encode("UTF-8")


@cherrypy.tools.register("before_finalize", priority=60)
def secureheaders():
    headers = cherrypy.response.headers
    headers["X-Frame-Options"] = "DENY"
    headers["X-XSS-Protection"] = "1; mode=block"
    headers["Content-Security-Policy"] = "default-src 'self';"


@cherrypy.popargs("action", "")
class AcInt(object):
    _cp_config = {
        "request.error_response": handle_an_exception,
        "error_page.default": handle_default,
    }

    @cherrypy.expose
    @cherrypy.tools.allow(methods=["POST"])
    @cherrypy.tools.json_in()
    def index(self):
        print("request", cherrypy.request.json)
        data = cherrypy.request.json
        if data["action"] not in allowed_actions:
            raise cherrypy.HTTPError(403, "Forbidden")
        if data["token"] != secure_token:
            raise cherrypy.HTTPError(403, "Forbidden")

        os.close(os.open(os.path.join(DO_PATH, data["action"]), os.O_CREAT))
        return f"Triggerd action {data['action']}."


if __name__ == "__main__":
    print("Allowed actions:", allowed_actions)
    print("Proxy path:", proxy_path)
    print("Token:", secure_token)
    print("Environment:", environment)
    cherrypy.config.update(
        {
            "server.socket_host": "0.0.0.0",
            "server.socket_port": 80,
        }
    )
    cherrypy.config.update(env_config["environments"][environment])
    cherrypy.quickstart(AcInt(), proxy_path)
