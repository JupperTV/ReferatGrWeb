#!/usr/bin/python
# * Was ist ein Event?
# Ein Event ist eine Veranstaltung, zu der sich Nutzer eintragen können.
# Beispiele: Vorlesungen, Online-Videokonferzen, Feier

import csv
from typing import Final, Iterable
from datetime import datetime
import uuid

import babel.dates

import errors
import entrymanager

class EventType:
    ON_SITE: Final[str] = "onsite"
    ONLINE: Final[str] = "online"

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
    EVENTTYPE: Final[EventType] = "type"
    
    # csv.DictWriter braucht die fieldnames der CSV Datei
    def AsList() -> list[str]:
        return [
            CSVHeader.EVENTID, CSVHeader.NAME, CSVHeader.EPOCH,
            CSVHeader.ORGANIZER_EMAIL, CSVHeader.COUNTRY, CSVHeader.CITY,
            CSVHeader.ZIPCODE, CSVHeader.STREET, CSVHeader.HOUSENUMBER,
            CSVHeader.DESCRIPTION]

class Event:
    def InitFromDict(dictionary: csv.DictReader | dict[str, str]):
        if len(dictionary) < 11:
            raise errors.NotEnoughElementsInListError()
        d = lambda h: dictionary.get(h)  # Weniger Boilerplate
        return Event(eventid=d(CSVHeader.EVENTID),
                     eventname=d(CSVHeader.NAME),
                     epoch=d(CSVHeader.EPOCH),
                     organizeremail=d(CSVHeader.ORGANIZER_EMAIL),
                     country=d(CSVHeader.COUNTRY),
                     zipcode=d(CSVHeader.ZIPCODE),
                     city=d(CSVHeader.CITY),
                     street=d(CSVHeader.STREET),
                     housenumber=d(CSVHeader.HOUSENUMBER),
                     description=d(CSVHeader.DESCRIPTION),
                     eventtype=d(CSVHeader.EVENTTYPE)
                     )

    def __init__(self, eventid: str, eventname: str, epoch: str,
                 organizeremail: str, country: str, city: str, zipcode: str,
                 street: str, housenumber: str, description: str, eventtype: str):
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
        self.eventtype=eventtype

    def __iter__(self):
        return iter([
            self.eventid, self.eventname, self.epoch, self.organizeremail,
            self.country, self.city, self.zipcode, self.street,
            self.housenumber, self.description, self.eventtype])

# Das ist nur zum ausgeben da, damiz nicht die Englischen Wörter da stehen
KEYS_FOR_OUTPUT = ["Eventnummer", "Eventname", "Datum",
           "Email des Veranstalters", "Land", "Stadt", "PLZ", "Strasse",
           "Hausnummer", "Beschreibung", "Eventtyp"]

_CSV_PATH: Final[str] = "data"
_CSV_EVENT: Final[str] = f"{_CSV_PATH}\\events.csv"

def _getdictreader_() -> csv.DictReader:
    entryfile_read = open(_CSV_EVENT, "r", newline="")
    return csv.DictReader(entryfile_read, delimiter=",")

def EpochToNormalTime(epoch: float | str) -> str:
    readabledate = datetime.fromtimestamp(float(epoch))
    return babel.dates.format_datetime(readabledate, locale="de_DE",
                                       format="dd.MM.yyyy 'um' HH:mm")

def GetAllEventsCreatedByOrganizer(organizeremail: str) -> list[Event]:
    reader = _getdictreader_()
    events: list[Event] = []
    for row in reader:
        if not row.values():
            continue
        if row.get(CSVHeader.ORGANIZER_EMAIL) == organizeremail:
            events.append(Event.InitFromDict(row))
    if not events:
        raise errors.AccountHasNoEventsError()
    return events

def GetAllEvents() -> list[Event]:
    return [Event.InitFromDict(row) for row in _getdictreader_()]

def EventExists(event: Event) -> bool:
    reader = _getdictreader_()
    for row in reader:
        if event == Event.InitFromDict(row):
            return True
    return False

def GetEventFromId(eventid) -> Event | None:
    reader = _getdictreader_()
    for row in reader:
        if eventid == row.get(CSVHeader.EVENTID):
            return Event.InitFromDict(row)
    return None

def IsTheSameEvent(*args) -> bool:
    reader = _getdictreader_()
    for row in reader:
        # Falls ein Benutzer die exakt selben Daten nochmal eingibt,
        # werden nur EventIDs unterschiedlich sein.
        # Deswegen werden sie hier nicht verglichen
        row.pop(CSVHeader.EVENTID)
        for index, header in enumerate(CSVHeader.AsList()):
            if args[index] != row.get(header):
                return False
    return True

def CreateEventFromForm(eventname, epoch: float, organizeremail, country, city,
                        zipcode: str, street, housenumber: str,
                        description: str, eventtype: EventType | str) -> None:
    SaveInCSV(eventid=uuid.uuid4(), eventname=eventname, epoch=epoch,
                    organizeremail=organizeremail, country=country, city=city,
                    zipcode=zipcode, street=street, housenumber=housenumber,
                    description=description, eventtype=eventtype)

def SaveInCSV(eventid, eventname, epoch, organizeremail, country, city, zipcode,
              street, housenumber, description, eventtype) -> None:
    if IsTheSameEvent(eventname, epoch, organizeremail, country, city, zipcode,
                      street, housenumber, description, eventtype):
        raise errors.EventAlreadyExistsError()
    eventfile_write = open(_CSV_EVENT, "a", newline="")
    # Es lohnt sich nicht, einen extra DictWriter zu benutzen, um nur
    # eine Zeile hinzuzufügen
    writer = csv.writer(eventfile_write, delimiter=",")
    writer.writerow([eventid, eventname, epoch, organizeremail, country, city,
                     zipcode, street, housenumber, description, eventtype])

# TODO
def ModifyEvent():
    return NotImplementedError()

def DeleteEvent(eventid):
    # Hier werden alle anderen Events (und die Überschriften) gelesen
    # und dann in die Datei überschrieben
    reader = _getdictreader_()
    newCSV: list[dict[str, str]] = []
    for row in reader:
        if not row.values():  # Zeile ist leer
            continue
        if row.get(CSVHeader.EVENTID) == eventid:
            continue
        newCSV.append(row)
    
    eventfile_write= open(_CSV_EVENT, "w", newline="")
    writer = csv.DictWriter(eventfile_write, fieldnames=CSVHeader.AsList(),
                            delimiter=",")
    writer.writerows(newCSV)

    entrymanager.DeleteAllEntriesWithEvent(eventid)
