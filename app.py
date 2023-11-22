from flask import Flask, request, abort, jsonify
from dataclasses import dataclass, field
from typing import List, Optional
from os import environ as env
from enum import Enum
import requests
import logging
import time

app = Flask(__name__)
logging.basicConfig(filename='webhook_logs.log', level=logging.INFO)

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

@dataclass
class Webhook:
    url: str
    ip_whitelist: List[str]
    ratelimit: int = 5
    requests: Optional[dict] = field(default=None)

class WebhookProtector:
    _webhook = Webhook(
        url=env['hook'],
        ip_whitelist=[""]
    )

    @classmethod
    def protect(cls, func):
        def wrapper(*args, **kwargs):
            cls._check_ip()
            cls._check_request_type()
            cls._update_request_history()
            return func(*args, **kwargs)
        return wrapper

    @classmethod
    def _check_ip(cls):
        client_ip = request.remote_addr
        if client_ip not in cls._webhook.ip_whitelist:
            cls._log_unauthorized_ip(client_ip)
            abort(403)
            return jsonify(error=True, message='unauthorized')

    @classmethod
    def _check_request_type(cls):
        if request.method == HttpMethod.DELETE.value:
            cls._log_unauthorized_request(request.method)
            abort(405)
            return jsonify(error=True, message='you can\'t do this action!')

    @classmethod
    def _update_request_history(cls):
        if cls._webhook.requests is None:
            cls._webhook.requests = {request.remote_addr: [time.time()]}
        else:
            cls._webhook.requests.setdefault(request.remote_addr, []).append(time.time())
            cls._webhook.requests[request.remote_addr] = [
                timestamp for timestamp in cls._webhook.requests[request.remote_addr]
                if timestamp >= time.time() - 60
            ][:cls._webhook.ratelimit]

            if len(cls._webhook.requests[request.remote_addr]) > cls._webhook.ratelimit:
                cls._log_ratelimited(request.remote_addr)
                abort(429)

    @classmethod
    def _log_unauthorized_ip(cls, ip):
        logging.info(f"Unauthorized IP: {ip} tried to access the webhook.")

    @classmethod
    def _log_unauthorized_request(cls, method):
        logging.info(f"Unauthorized request method: {method} received.")

    @classmethod
    def _log_ratelimited(cls, ip):
        logging.info(f"IP: {ip} exceeded the rate limit.")

@app.route('/', methods=['POST'])
@WebhookProtector.protect
def handle_hook():
    payload = request.get_json()
    logging.info(f"Received POST data: {payload}")
      
    response = requests.post(str(WebhookProtector._webhook.url), json=dict(payload))

    logging.info(f"Response from Discord webhook: {response.status_code}")
    result = response.status_code == 204
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=80)
