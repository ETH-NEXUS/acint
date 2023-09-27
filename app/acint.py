#!/usr/bin/env python3

import cherrypy
import os

DO_PATH = os.path.join(os.path.sep, "do")
os.makedirs(DO_PATH, exist_ok=True)

allowed_actions_string = os.environ.get("ACINT_ALLOWED_ACTIONS", "").strip()
if len(allowed_actions_string) == 0:
    allowed_actions = [".deploy"]
else:
    allowed_actions = os.environ.get("ACINT_ALLOWED_ACTIONS", ".deploy").split(",")
proxy_path = os.environ.get("ACINT_PROXY_PATH", None) or "/acint"


def handle_an_exception():
    cherrypy.response.status = 500
    cherrypy.response.headers["content-type"] = "text/plain;charset=UTF-8"
    cherrypy.response.body = b"Internal Server Error"


def handle_default(status=None, message=None, version=None, traceback=None):
    cherrypy.response.headers["content-type"] = "text/plain;charset=UTF-8"
    return f"{status}".encode("UTF-8")


@cherrypy.popargs("action")
class AcInt(object):
    _cp_config = {
        # handler for an unhandled exception
        "request.error_response": handle_an_exception,
        # default handler for any other HTTP error
        "error_page.default": handle_default,
    }

    @cherrypy.expose
    def index(self, action=None):
        if action not in allowed_actions:
            raise cherrypy.HTTPError(403, "Forbidden")
        os.close(os.open(os.path.join(DO_PATH, action), os.O_CREAT))
        return f"Triggerd action {action}."


if __name__ == "__main__":
    print("Allowed actions:", allowed_actions)
    print("Proxy path:", proxy_path)
    cherrypy.config.update(
        {
            "server.socket_host": "0.0.0.0",
            "server.socket_port": 80,
            "engine.autoreload.on": False,
            "checker.on": False,
            "tools.log_headers.on": False,
            "request.show_tracebacks": False,
            "request.show_mismatched_params": False,
            "log.screen": False,
        }
    )
    cherrypy.quickstart(AcInt(), proxy_path)
