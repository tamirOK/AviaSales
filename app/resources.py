from http import HTTPStatus

from flask_restful import Resource, fields, marshal_with, abort, reqparse

from app import app, db
from .extract import FlightType
from .models import Route

ticket_fields = {
    "carrier_id": fields.String,
    "flight_number": fields.String,
    "source": fields.String,
    "destination": fields.String,
    "departure_time": fields.DateTime,
    "arrival_time": fields.DateTime,
    "class_": fields.String,
    "ticket_type": fields.String,
}

route_fields = {
    "id": fields.String,
    "carrier_id": fields.String,
    "source": fields.String,
    "destination": fields.String,
    "departure_time": fields.DateTime,
    "arrival_time": fields.DateTime,
    "duration": fields.String,
    "adult_price": fields.String,
    "child_price": fields.String,
    "infant_price": fields.String,
    "currency": fields.String,
    "flight_type": fields.String,
    "back_departure_time": fields.String,
    "back_arrival_time": fields.String,
    "tickets": fields.List(fields.Nested(ticket_fields))
}


class RouteResource(Resource):
    @marshal_with(route_fields)
    def get(self, route_id):
        try:
            route = db.session.query(Route).filter(Route.id == route_id).first()
            if not route:
                abort(HTTPStatus.NOT_FOUND.value, message=f"Route {route_id} does not exist")
            return route
        except:
            db.session.rollback()
        finally:
            db.session.close()


class RouteListResource(Resource):

    parser = reqparse.RequestParser(bundle_errors=True)
    parser.add_argument("page", type=int, location="args", default=1,
                        help="page must be positive integer")
    parser.add_argument("flight_type", type=str, location="args",
                        choices=("one_way", "two_way"), default="one_way",
                        help="flight type must be one of: one_way, two_way")
    parser.add_argument("order_by", type=str, location="args",
                        choices=("duration", "price"), default="duration",
                        help="order_by must be one of: duration, price")

    @marshal_with(route_fields)
    def get(self):
        args = self.parser.parse_args()
        flight_type = FlightType.ONE_WAY if args["flight_type"] == "one_way" else FlightType.TWO_WAY
        order_type = Route.duration if args["order_by"] == "duration" else Route.adult_price
        routes = db.session.query(Route).filter(
            Route.flight_type == flight_type).order_by(order_type).paginate(
            args["page"], app.config["POSTS_PER_PAGE"], False
        ).items
        return routes
