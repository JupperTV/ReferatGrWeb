#!/usr/bin/python
# * Was ist ein Event?
# Ein Event ist eine Veranstaltung, zu der sich Nutzer eintragen können.
# Beispiele: Vorlesungen, Online-Videokonferzen, Feier

import csv
from typing import Final, Iterable, TypedDict
from datetime import datetime
import uuid

import babel.dates

import errors
import entrymanager

# * Vielleicht ist es sogar besser, das zu einem TypedDict umzuwandeln
class Event:
    def InitFromList(elements: list[str]):
        if len(elements) < 10:
            raise errors.NotEnoughElementsInListError()
        return Event(*elements)

    def __init__(self, eventid: str, eventname: str, epoch: str,
                 organizeremail: str, country: str, city: str, zipcode: str,
                 street: str, housenumber: str, description: str):
        self.eventid = eventid
        self.eventname = eventname
        self.epoch = epoch
        self.organizeremail = organizeremail
        self.country = country
        self.city = city
        self.zipcode = zipcode
        self.street = street
        self.housenumber = housenumber
        self.description = description

    def __iter__(self):
        return iter([
            self.eventid, self.eventname, self.epoch, self.organizeremail,
            self.country, self.city, self.zipcode, self.street,
            self.housenumber, self.description])

class CSVHeader:
    EVENTID: Final[str] = "id"
    NAME: Final[str] = "name"
    EPOCH: Final[str] = "epoch"
    ORGANIZER_EMAIL: Final[str] = "organizer"
    COUNTRY: Final[str] = "country"
    CITY: Final[str] = "city"
    ZIPCODE: Final[str] = "zipcode"
    STREET: Final[str] = "street"
    HOUSENUMBER: Final[str] = "housenumber"
    DESCRIPTION: Final[str] = "description"

# KEYS_DE ist nur zum ausgeben gedacht
KEYS_FOR_OUTPUT = ["Eventnummer", "Eventname", "Datum",
           "Email des Veranstalters", "Land", "Stadt", "PLZ", "Strasse",
           "Hausnummer", "Beschreibung"]

_CSV_PATH: Final[str] = "data"
_CSV_EVENT: Final[str] = f"{_CSV_PATH}\\events.csv"

# To reduce boilerplate
# def _getreader_() -> Iterable[list[str]]:
#     eventfile_read = open(_CSV_EVENT, "r", newline="")
#     return csv.reader(eventfile_read, delimiter=",")

# TODO: Alle reader in dictreader umwandeln
# * Ein csv.DictReader funktioniert im Prinzip wie ein list[dict[str, str]]
def _getdictreader_() -> csv.DictReader:
    entryfile_read = open(_CSV_EVENT, "r", newline="")
    return csv.DictReader(entryfile_read, delimiter=",")


def EpochToNormalTime(epoch: float | str) -> str:
    readabledate = datetime.fromtimestamp(float(epoch))
    return babel.dates.format_datetime(readabledate, locale="de_DE",
                                       format="dd.MM.yyyy 'um' HH:mm")

# TODO: Test
def GetAllEventsCreatedByOrganizer(organizeremail: str) -> list[Event]:
    reader = _getdictreader_()
    next(reader)  # Skip Headers
    events: list[Event] = []
    for row in reader:
        if not row.values():
            continue
        if row.get(CSVHeader.ORGANIZER_EMAIL) == organizeremail:
            events.append(Event.InitFromList(row))
    if not events:
        raise errors.AccountHasNoEventsError()
    return events

# TODO: Test
def GetAllEvents() -> list[Event]:
    reader = _getdictreader_()
    allEvents: list[Event] = []
    for row in reader:
        allEvents.append(Event.InitFromList(row.values()))
    return allEvents

# TODO: Test
def EventExists(event: Event) -> bool:
    reader = _getdictreader_()
    for row in reader:
        if event == Event.InitFromList(row.values()):
            return True
    return False

# TODO: Test
def GetEventFromId(eventid) -> Event | None:
    reader = _getdictreader_()
    for row in reader:
        if eventid == row.get(CSVHeader.EVENTID):
            return Event.InitFromList(row.values())
    return None

def CreateEventFromForm(eventname, epoch: float, organizeremail, country, city,
                        zipcode: str, street, housenumber: str,
                        description) -> None:
    eventid = uuid.uuid4()
    SaveInCSV(Event(eventid=eventid, eventname=eventname, epoch=epoch,
                    organizeremail=organizeremail, country=country, city=city,
                    zipcode=zipcode, street=street, housenumber=housenumber,
                    description=description))

def SaveInCSV(event: Event) -> None:
    if EventExists(event):
        raise errors.EventAlreadyExistsError()
    eventfile_write = open(_CSV_EVENT, "a", newline="")
    writer = csv.writer(eventfile_write, delimiter=",")
    writer.writerow(list(event))

# TODO
def ModifyEvent():
    return NotImplementedError()

# TODO: Test
def DeleteEvent(eventid):
    reader = _getdictreader_()
    newCSV: list[dict[str, str]] = []
    for row in reader:
        if not row.values():
            continue
        if row.get(CSVHeader.EVENTID) == eventid:
            continue
        newCSV.append(row)
    
    eventfile_write= open(_CSV_EVENT, "w", newline="")
    writer = csv.DictWriter(eventfile_write, delimiter=",")
    writer.writerows(newCSV)

    entrymanager.DeleteAllEntriesWithEvent(eventid)

