#!/usr/bin/python
# * Was ist ein Event?
# Ein Event ist eine Veranstaltung, zu der sich Nutzer eintragen können.
# Beispiele: Vorlesungen, Online-Videokonferzen, Feier

import csv
from typing import Final, Iterable, TypedDict
import uuid

import errors

# * Vielleicht ist es sogar besser, das zu einem TypedDict umzuwandeln
# TODO: Test
class Event:
    def InitFromList(elements: list[str]):
        if len(elements) < 9:
            raise errors.NotEnoughElementsInListError()
        return Event(*elements)

    def __init__(self, eventid, eventname, epoch, organizer, country, city, zipcode, street, housenumber):
        self.eventid = eventid
        self.eventname = eventname
        self.epoch = epoch
        self.organizer = organizer
        self.country = country
        self.city = city
        self.zipcode = zipcode
        self.street = street
        self.housenumber = housenumber

    def __iter__(self):
        return iter([
            self.eventid, self.eventname, self.epoch, self.organizer,
            self.country, self.city, self.zipcode, self.street, self.housenumber])

KEYS = ["eventid", "eventname", "epoch", "organizer", "country", "citry", "zipcode", "street", "housenumber"]

_CSV_PATH: Final[str] = "data"
_CSV_EVENT: Final[str] = f"{_CSV_PATH}\\events.csv"

# To reduce boilerplate
def _getcsvreader_() -> Iterable[list[str]]:
    eventfile_read = open(_CSV_EVENT, "r", newline="")
    return csv.reader(eventfile_read, delimiter=",")


# TODO: Test
def GetAllEvents() -> list[Event]:  # * Replace tuple with the Entry Class???
    reader = list(filter(None, list(_getcsvreader_())))  # Filtere zuerst leere Listen aus
    allEvents: list[Event] = []
    if len(reader) < 2 or not reader[1]:
        return []
    for row in reader[1:]:
        allEvents.append(Event.InitFromList(row))  # row[0] ist die id, was nicht angezeigt werden soll
    return allEvents

# TODO: Test
def GetEventsByName(name: str) -> list[Event]:  # * Replace tuple with the Entry Class???
    """Get all of the events that have the same name"""
    reader = _getcsvreader_()
    allEvents: list[Event] = []
    for row in reader:
        if (row) and (name in row):  # ```if row``` == row ist nicht leer
            allEvents.append(Event.InitFromList(row))
    return allEvents

# TODO: Test
def EventExists(event: Event) -> bool:
    reader: Iterable = _getcsvreader_()
    next(reader)  # Überspringe Header
    for row in reader:
        if event == Event.InitFromList(row):
            return True
    return False

# TODO: Test
def CreateEventFromForm(eventname, epoch: float, organizeremail, country, city,
                        zipcode: str, street, housenumber: str) -> None:
    eventid = uuid.uuid4()
    # eventid, eventname, epoch, organizer, country, city, zipcode, street, housenumber
    SaveEvent(Event(eventid=eventid, eventname=eventname, epoch=epoch,
                    organizer=organizeremail, country=country, city=city,
                    zipcode=zipcode, street=street, housenumber=housenumber))


# TODO: Test
def SaveEvent(event: Event) -> None:
    if EventExists(event):
        raise errors.EventAlreadyExistsError()
    eventfile_read = open(_CSV_EVENT, "a", newline="")  # Vielleicht _getwriter()_?
    writer = csv.writer(eventfile_read, delimiter=",")
    writer.writerow(list(event))

def ModifyEvent():
    return NotImplementedError()

def DeleteEvent():
    return NotImplementedError()
