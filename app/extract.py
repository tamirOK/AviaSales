from decimal import Decimal
import itertools as it

from datetime import datetime

from app import db
import click
from .models import Ticket, Route

import xml.etree.ElementTree as ET


class FlightType:
    ONE_WAY = "ONE_WAY"
    TWO_WAY = "TWO_WAY"


class PriceType:
    ADULT = "SingleAdult"
    CHILD = "SingleChild"
    INFANT = "SingleInfant"


def get_flights(itinerary):
    """
    Returns all flights info for "OnwardPricedItinerary" and "ReturnPricedItinerary" tags
    """
    dt_format = "%Y-%m-%dT%H%M"
    onward_flights = []
    for flight in itinerary[0]:  # Flights
        extracted_data = {item.tag: item.text for item in flight}
        onward_flights.append(Ticket(
            carrier_id=extracted_data["Carrier"],
            flight_number=extracted_data["FlightNumber"],
            source=extracted_data["Source"],
            destination=extracted_data["Destination"],
            departure_time=datetime.strptime(extracted_data["DepartureTimeStamp"], dt_format),
            arrival_time=datetime.strptime(extracted_data["ArrivalTimeStamp"], dt_format),
            class_=extracted_data["Class"],
            number_of_stops=extracted_data["NumberOfStops"],
            fare_basis=extracted_data["FareBasis"],
            ticket_type=extracted_data["TicketType"],
            warning_text=extracted_data["WarningText"]
            ))
    return sorted(onward_flights, key=lambda ticket: ticket.departure_time)


def get_prices(pricing):
    """
    Extracts extracts all prices from "Pricing" tag
    """
    prices = {
        PriceType.ADULT: 0,
        PriceType.CHILD: 0,
        PriceType.INFANT: 0
    }
    for price in pricing:
        if price.attrib.get("ChargeType") == "TotalAmount":
            prices[price.attrib.get("type")] = Decimal(price.text)
    return prices


def extract(two_way=True):
    """
        extracts data from via3.xml, viaow.xml and saves it to DB
    """
    file_name = "via3.xml" if two_way else "viaow.xml"
    tree = ET.parse(file_name)
    root = tree.getroot()
    flight_type = FlightType.TWO_WAY if two_way else FlightType.ONE_WAY

    for flight in root.findall("./PricedItineraries/Flights"):
        onwards = get_flights(flight[0])  # onward flights
        prices_child_pos = 2 if two_way else 1
        currency = flight[prices_child_pos].attrib.get("currency")
        backwards = get_flights(flight[1]) if two_way else []  # backward flights
        prices = get_prices(flight[prices_child_pos])
        source = onwards[0]
        final_destination = onwards[-1]
        duration = (final_destination.arrival_time - source.departure_time).total_seconds()
        route = Route(
            carrier_id=source.carrier_id,
            source=source.source,
            destination=final_destination.destination,
            departure_time=source.departure_time,
            arrival_time=final_destination.arrival_time,
            duration=duration,
            adult_price=prices[PriceType.ADULT],
            child_price=prices[PriceType.CHILD],
            infant_price=prices[PriceType.INFANT],
            currency=currency,
            flight_type=flight_type
        )
        if two_way:
            route.back_departure_time = backwards[0].departure_time
            route.back_arrival_time = backwards[-1].arrival_time
        db.session.add(route)
        for ticket in it.chain(onwards, backwards):
            ticket = db.session.merge(ticket)
            route.tickets.append(ticket)
    db.session.commit()


@click.command()
def populate_db():
    """
    Extracts data from xml files and puts into db
    """
    db.create_all()
    extract()
    extract(two_way=False)
