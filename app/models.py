from app import db


connection_table = db.Table("connection",
    db.Column("carrier_id", db.String(50), nullable=False),
    db.Column("flight_number", db.Integer, nullable=False),
    db.Column("departure_time", db.DateTime, nullable=False),
    db.Column("route_id", db.Integer, db.ForeignKey("routes.id")),
    db.ForeignKeyConstraint(['carrier_id', 'flight_number', 'departure_time'],
                         ['tickets.carrier_id', 'tickets.flight_number',
                          'tickets.departure_time'])
)


class Ticket(db.Model):
    """
        Stores details about ticket
    """
    __tablename__ = "tickets"

    carrier_id = db.Column(db.String(50), primary_key=True)
    flight_number = db.Column(db.Integer, nullable=False, primary_key=True)
    source = db.Column(db.String(10), nullable=False)
    destination = db.Column(db.String(10), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False, primary_key=True)
    arrival_time = db.Column(db.DateTime, nullable=False)
    class_ = db.Column(db.String(1), nullable=False)
    number_of_stops = db.Column(db.Integer, nullable=False)
    fare_basis = db.Column(db.String(200), nullable=False)
    ticket_type = db.Column(db.String(1), nullable=False)
    warning_text = db.Column(db.String)


class Route(db.Model):
    """
        Contains general data about route
    """
    __tablename__ = "routes"

    id = db.Column(db.Integer, primary_key=True)
    carrier_id = db.Column(db.String(10), nullable=False)
    source = db.Column(db.String(10), nullable=False)
    destination = db.Column(db.String(10), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=0)  # duration of flight in seconds
    adult_price = db.Column(db.Numeric(precision=20, scale=10), default=0)
    child_price = db.Column(db.Numeric(precision=20, scale=10), default=0)
    infant_price = db.Column(db.Numeric(precision=20, scale=10), default=0)
    currency = db.Column(db.String(3), nullable=False)
    flight_type = db.Column(db.String(5), nullable=False)  # one way or with return
    back_departure_time = db.Column(db.DateTime, nullable=True)  # if there is return flight
    back_arrival_time = db.Column(db.DateTime, nullable=True)  # if there is return flight

    tickets = db.relationship(
        "Ticket", secondary=connection_table, lazy="joined", innerjoin=True,
        order_by="Ticket.departure_time"
    )
