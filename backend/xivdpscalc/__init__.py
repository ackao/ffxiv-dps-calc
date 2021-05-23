"""ffxiv-dps-calc – dps calculations for the smart masses"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('xivdpscalc.config')
db = SQLAlchemy(app)
CORS(app)

if __name__ == "__main__":
    app.run()

import xivdpscalc.routing #pylint: disable=wrong-import-position
