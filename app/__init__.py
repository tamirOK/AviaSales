from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
api = Api(app)
db = SQLAlchemy(app)

from .resources import RouteResource, RouteListResource
from .extract import populate_db

api.add_resource(RouteResource, "/routes/<int:route_id>/")
api.add_resource(RouteListResource, "/routes/")

app.cli.add_command(populate_db)

if __name__ == "__main__":
    app.run(debug=True)
