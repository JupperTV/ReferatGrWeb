#!/usr/bin/python

# * What is an event?
# An event is an event that users can register to
# Examples: Lectures, Videocalls, Meetings

import csv
from typing import Final, Iterable
import time
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
    EVENTTYPE: Final[EventType] = "type"
    ORGANIZER_EMAIL: Final[str] = "organizer"
    COUNTRY: Final[str] = "country"
    CITY: Final[str] = "city"
    ZIPCODE: Final[str] = "zipcode"
    STREET: Final[str] = "street"
    HOUSENUMBER: Final[str] = "housenumber"
    DESCRIPTION: Final[str] = "description"

    # csv.DictWriter needs the fieldnames of the CSV file
    def AsList() -> list[str]:
        return [CSVHeader.EVENTID, CSVHeader.NAME, CSVHeader.EPOCH,
                CSVHeader.EVENTTYPE, CSVHeader.ORGANIZER_EMAIL, CSVHeader.COUNTRY,
                CSVHeader.CITY, CSVHeader.ZIPCODE, CSVHeader.STREET,
                CSVHeader.HOUSENUMBER, CSVHeader.DESCRIPTION]

class Event:
    def InitFromDict(dictionary: csv.DictReader | dict[str, str]):
        if len(dictionary) < 11:
            raise errors.NotEnoughElementsInListError()
        d = lambda h: dictionary.get(h)  # Less boilerplate
        return Event(eventid=d(CSVHeader.EVENTID),
                     eventname=d(CSVHeader.NAME),
                     epoch=d(CSVHeader.EPOCH),
                     eventtype=d(CSVHeader.EVENTTYPE),
                     organizeremail=d(CSVHeader.ORGANIZER_EMAIL),
                     country=d(CSVHeader.COUNTRY),
                     zipcode=d(CSVHeader.ZIPCODE),
                     city=d(CSVHeader.CITY),
                     street=d(CSVHeader.STREET),
                     housenumber=d(CSVHeader.HOUSENUMBER),
                     description=d(CSVHeader.DESCRIPTION)
                     )

    def __init__(self, eventid: str, eventname: str, epoch: str, eventtype: str,
                 organizeremail: str, country: str, city: str, zipcode: str,
                 street: str, housenumber: str, description: str):
        self.eventid = eventid
        self.eventname = eventname
        self.epoch = epoch
        self.eventtype=eventtype
        self.organizeremail = organizeremail
        self.country = country
        self.city = city
        self.zipcode = zipcode
        self.street = street
        self.housenumber = housenumber
        self.description = description

    def __iter__(self):
        return iter([
            self.eventid, self.eventname, self.epoch, self.eventtype,
            self.organizeremail, self.country, self.city, self.zipcode,
            self.street, self.housenumber, self.description])

# This only exists for displaying information on the frontend
KEYS_FOR_OUTPUT = ["Event number", "Eventname", "Date", "Event type",
           "Organizer e-mail", "Country", "City", "Zipcode", "Street",
           "House number", "Description"]

def GetReadableEventType(eventtype: str) -> str:
    return "On site" if eventtype == EventType.ON_SITE else "Online"


_CSV_PATH: Final[str] = "data"
_CSV_EVENT: Final[str] = f"{_CSV_PATH}\\events.csv"

def _getdictreader_() -> csv.DictReader:
    eventfile_read = open(_CSV_EVENT, "r", newline="")
    return csv.DictReader(eventfile_read, delimiter=",")

def EpochToNormalTime(epoch: float | str) -> str:
    readabledate = datetime.fromtimestamp(float(epoch))
    return babel.dates.format_datetime(readabledate, locale="de_DE",
                                       format="dd.MM.yyyy 'um' HH:mm")

def EpochToInputTime(epoch: float | str):
    return time.strftime("%Y-%m-%dT%H:%M", time.localtime(float(epoch)))

def InputTimeToEpoch(inputtime: str):
    return float(time.mktime(time.strptime(inputtime, "%Y-%m-%dT%H:%M")))

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
    reader = list(_getdictreader_())
    if not reader:
        return False
    for row in reader:
        # If a user enters the exact same data of another event, then
        # the eventids will be the only thing difference.
        # That's why they aren't being compared
        row.pop(CSVHeader.EVENTID)
        for index, header in enumerate(CSVHeader.AsList()):
            if args[index] != row.get(header):
                return False
    return True

def CreateEventFromForm(eventname, epoch: float, eventtype: str, organizeremail,
                        country, city, zipcode: str, street, housenumber: str,
                        description: str) -> None:
    SaveInCSV(eventid=uuid.uuid4(), eventname=eventname, epoch=epoch,
              eventtype=eventtype, organizeremail=organizeremail, country=country,
              city=city, zipcode=zipcode, street=street, housenumber=housenumber,
              description=description)

def SaveInCSV(eventid, eventname, epoch, eventtype, organizeremail, country, city, zipcode,
              street, housenumber, description) -> None:
    if IsTheSameEvent(eventname, epoch, eventtype, organizeremail, country, city, zipcode,
                      street, housenumber, description, eventtype):
        raise errors.EventAlreadyExistsError()
    eventfile_write = open(_CSV_EVENT, "a", newline="")
    # It's not worth it to use a DictWriter just to insert a new dataset
    writer = csv.writer(eventfile_write, delimiter=",")
    writer.writerow([eventid, eventname, epoch,eventtype, organizeremail,
                     country, city, zipcode, street, housenumber, description])

def ModifyEvent(event: Event) -> None:
    reader: list[dict] = list(_getdictreader_())
    for row in reader:
        if row.get(CSVHeader.EVENTID) == event.eventid:
            for index, header in enumerate(CSVHeader.AsList()):
                reader[reader.index(row)][header] = list(event)[index]
            break  # The event has been found

    eventfile_write = open(_CSV_EVENT, "w", newline="")
    writer = csv.DictWriter(eventfile_write, fieldnames=CSVHeader.AsList())
    writer.writerow(dict(zip(CSVHeader.AsList(), CSVHeader.AsList())))
    writer.writerows(reader)

def DeleteEvent(eventid):
    # Every other row including the headers, other than the row of the
    # event that needs to be deleted, are read and then overwriten to
    # the file
    reader = _getdictreader_()
    newCSV: list[dict[str, str]] = []
    for row in reader:
        if not row.values():  # row is empty
            continue
        if row.get(CSVHeader.EVENTID) == eventid:
            continue
        newCSV.append(row)

    eventfile_write = open(_CSV_EVENT, "w", newline="")
    writer = csv.DictWriter(eventfile_write, fieldnames=CSVHeader.AsList(),
                            delimiter=",")

    writer.writerow(dict(zip(CSVHeader.AsList(), CSVHeader.AsList())))
    writer.writerows(newCSV)

    entrymanager.DeleteAllEntriesWithEvent(eventid)

