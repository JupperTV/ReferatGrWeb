#!/usr/bin/python
# * Was ist ein Event?
# Ein Event ist eine Veranstaltung, zu der sich Nutzer eintragen können.
# Beispiele: Vorlesungen, Online-Treffs

import csv
from typing import Final, Iterable, TypedDict
import uuid

import .errors

# * Vielleicht ist es sogar besser, das zu einem TypedDict umzuwandeln
class Events:
    def InitFromList(elements: list[str]):
        if len(list) < 8:
            raise errors.NotEnoughElementsInListError()
        return __init__(self, *elements)

    def __init__(self, eventid, name, organizer, country, city, zipcode, street, housenumber):
        self.eventid = eventid
        self.name = name
        self.organizer = organizer
        self.country = country
        self.city = city
        self.zipcode = zipcode
        self.street = street
        self.housenumber = housenumber

_CSV_PATH: Final[str] = "data"
_CSV_EVENT: Final[str] = f"{_CSV_PATH}\\events.csv"

# To reduce boilerplate
def _getreader_() -> Iterable[list[str]]:
    eventfile_read = open(_CSV_EVENT, "r", newline="")
    return csv.reader(eventfile_read, delimiter=",")

def GetAllEvents() -> list[Events]:  # * Replace tuple with the Entry Class???
    reader = filter(None, list(_getreader_()))  # Filtere zuerst leere Listen aus
    allEvents: list[Events] = []
    print(reader)
    if len(reader) < 2 or not reader[1]:
        return []
    for row in reader[1:]:
        allEvents.append(row[1:])  # row[0] ist die id, was nicht angezeigt werden soll
    return allEvents

def GetEventsByName(name: str) -> list[Events]:  # * Replace tuple with the Entry Class???
    """Get all of the events that have the same name"""
    reader = _getreader_()
    allEvents: list[Events] =
    for row in reader:
        if row and name in row:  # ```if row``` == row ist nicht leer
            allEvents.append(Events.InitFromList(row))
    return allEvents

def EventExists(name: str, epochtime: float) -> bool:
    reader = _getreader_()
    next(reader)  # Überspringe Header
    for row in reader:
        if row[1] != name:
            continue
        if float(row[2]) == epochtime:
            return True
    return False

def CreateEvent(name: str, epochtime: float) -> None:
    if EventExists(name, epochtime):
        raise errors.EventAlreadyExistsError()
    eventfile_read = open(_CSV_EVENT, "r", newline="")
    writer = csv.writer(eventfile_read, delimiter=",")
    writer.writerow([uuid.uuid4(), name, epochtime])

def ModifyEvent():
    return NotImplementedError()

def DeleteEvent():
    return NotImplementedError()
