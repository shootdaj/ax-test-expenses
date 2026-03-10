from flask import Flask

app = Flask(__name__)

from app import dashboard, routes  # noqa: E402, F401
