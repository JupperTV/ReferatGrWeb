#!/usr/bin/python
# * Was ist ein Event?
# Ein Event ist eine Veranstaltung, zu der sich Nutzer eintragen können.
# Beispiele: Vorlesungen, Online-Videokonferzen, Feier

import csv
from typing import Final, Iterable, TypedDict
import uuid

import errors
import entrymanager

# * Vielleicht ist es sogar besser, das zu einem TypedDict umzuwandeln
class Event:
    def InitFromList(elements: list[str]):
        if len(elements) < 10:  # In der Zukunft + 1 für die Beschreibung
            raise errors.NotEnoughElementsInListError()
        return Event(*elements)

    def __init__(self, eventid: str, eventname: str, epoch: str,
                 organizer: str, country: str, city: str, zipcode: str,
                 street: str, housenumber: str, description: str):
        self.eventid = eventid
        self.eventname = eventname
        self.epoch = epoch
        self.organizer = organizer
        self.country = country
        self.city = city
        self.zipcode = zipcode
        self.street = street
        self.housenumber = housenumber
        self.description = description

    def __iter__(self):
        return iter([
            self.eventid, self.eventname, self.epoch, self.organizer,
            self.country, self.city, self.zipcode, self.street,
            self.housenumber, self.description])

KEYS_DE = ["Eventnummer", "Eventname", "Zeit in Epoch",
           "Email des Veranstalters", "Land", "Stadt", "PLZ", "Strasse",
           "Hausnummer", "Beschreibung"]

_CSV_PATH: Final[str] = "data"
_CSV_EVENT: Final[str] = f"{_CSV_PATH}\\events.csv"

# To reduce boilerplate
def _getreader_() -> Iterable[list[str]]:
    eventfile_read = open(_CSV_EVENT, "r", newline="")
    return csv.reader(eventfile_read, delimiter=",")

def GetAllEventsCreatedByOrganizer(organizeremail: str) -> list[Event]:
    reader = _getreader_()
    next(reader)  # Skip Headers
    INDEX_OF_EMAIL: Final[int] = 3
    events: list[Event] = []
    for row in reader:
        if not row:
            continue
        if row[INDEX_OF_EMAIL] == organizeremail:
            events.append(Event.InitFromList(row))
    if not events:
        raise errors.AccountHasNoEventsError()
    return events

def GetAllEvents() -> list[Event]:  # Event mit TypedDict ersetzen?
    reader = list(filter(None, list(_getreader_())))  # Filtere zuerst leere Listen aus
    allEvents: list[Event] = []
    if len(reader) < 2 or not reader[1]:
        return []
    for row in reader[1:]:
        allEvents.append(Event.InitFromList(row))  # row[0] ist die id, was nicht angezeigt werden soll
    return allEvents

def EventExists(event: Event) -> bool:
    reader: Iterable = _getreader_()
    next(reader)  # Überspringe Header
    for row in reader:
        if event == Event.InitFromList(row):
            return True
    return False


def GetEventFromId(eventid) -> Event | None:
    reader: Iterable[str] = _getreader_()
    next(reader)  # Überspringe Header
    for row in reader:
        if eventid == row[0]:
            return Event.InitFromList(row)
    return None

def CreateEventFromForm(eventname, epoch: float, organizeremail, country, city,
                        zipcode: str, street, housenumber: str,
                        description: str) -> None:
    eventid = uuid.uuid4()
    # eventid, eventname, epoch, organizer, country, city, zipcode, street, housenumber
    SaveEvent(Event(eventid=eventid, eventname=eventname, epoch=epoch,
                    organizer=organizeremail, country=country, city=city,
                    zipcode=zipcode, street=street, housenumber=housenumber,
                    description=description))

def SaveEvent(event: Event) -> None:
    if EventExists(event):
        raise errors.EventAlreadyExistsError()
    eventfile_read = open(_CSV_EVENT, "a", newline="")
    writer = csv.writer(eventfile_read, delimiter=",")
    writer.writerow(list(event))

# TODO
def ModifyEvent():
    return NotImplementedError()

# TODO
def DeleteEvent(eventid):
    reader = list(_getreader_())
    rowtoremove: list[str] = []
    if not reader[1:]:
        raise errors.AccountHasNoEventsError()
    for row in reader[1:]:
        if row[0] == eventid:
            rowtoremove = row
            break
    reader.remove(rowtoremove)
    # ! Important Note: The file will be completely deleted after this
    # ! We will completely rewrite it
    csvfile = open(_CSV_EVENT, "w", newline="")
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerows(reader)

    entrymanager.DeleteAllEntriesWithEvent(eventid)

