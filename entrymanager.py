#!/usr/bin/python
# * What is an Entry?
# An entry is what connects an account with an event.
# If, for example, a user registers for an event, then this is
# is saved as an entry/registration for this event

import csv
from typing import Final, Iterable
import uuid

import eventmanager
import errors

_CSV_PATH: Final[str] = "data"
_CSV_ENTRY: Final[str] = f"{_CSV_PATH}\\entries.csv"

# * Note:
# * I don't have a class for the entries, like I did for the accounts
# * and the events, because a dataset consists of 3 ids anyway.

class CSVHeader:
    ENTRYID: Final[str] = "id"
    ACCOUNTID: Final[str] = "accountid"
    EVENTID: Final[str] = "eventid"
    def AsList() -> list[str]:
        return [CSVHeader.ENTRYID, CSVHeader.ACCOUNTID, CSVHeader.EVENTID]

def _getdictreader_() -> csv.DictReader:
    entryfile_read = open(_CSV_ENTRY, "r", newline="")
    return csv.DictReader(entryfile_read, delimiter=",")

def SaveInCSV(accountid: int, eventid: int) -> None:
    entryfile_writer = open(_CSV_ENTRY, "a", newline="")
    # A Dictwriter isn't worth it here because I would have to zip the 3
    # variables with CSVHeader.AsList() and that's too much work for so
    # little
    writer = csv.writer(entryfile_writer, delimiter=",")
    entryid = uuid.uuid4()
    writer.writerow([entryid, accountid, eventid])

def DidAccountAlreadyEnter(accountid, eventid) -> bool:
    reader = _getdictreader_()
    for row in reader:
        if not row.values():  # row is empty
            continue
        if row.get(CSVHeader.ACCOUNTID) == accountid \
            and row.get(CSVHeader.EVENTID) == eventid:
            return True
    return False

def GetAllEntriedEventsOfAccount(accountid) -> list[eventmanager.Event] | None:
    events: list[eventmanager.Event] = eventmanager.GetAllEvents()
    reader = _getdictreader_()
    if not reader:
        return None
    entriedevents: list[eventmanager.Event] = []
    for row in reader:
        if row.values() and row.get(CSVHeader.ACCOUNTID) == accountid:
            entriedevents.append(eventmanager.GetEventFromId(row.get(CSVHeader.EVENTID)))
    return entriedevents

def DeleteAllEntriesWithEvent(eventid) -> None:
    events: list[eventmanager.Event] = eventmanager.GetAllEvents()
    reader: csv.DictReader = _getdictreader_()
    rowsWithoutEvent: list[dict[str, str]] = []
    for row in reader:
        if not row.values():
            continue
        if row.get(CSVHeader.EVENTID) == eventid:
            continue
        rowsWithoutEvent.append(row)

    # * Important Note:
    # The file will be deleted immediately after being opened.
    # writer.writerows() will completely overwrite it
    entryfile_write = open(_CSV_ENTRY, "w", newline="")
    writer = csv.DictWriter(entryfile_write, fieldnames=CSVHeader.AsList(),
                            delimiter=",")
    writer.writerow(dict(zip(CSVHeader.AsList(), CSVHeader.AsList())))
    writer.writerows(rowsWithoutEvent)

def DeleteEntry(accountid: int, eventid: int) -> None:
    reader = _getdictreader_()
    newCSV: list[dict[str, str]] = []
    for row in reader:
        if not row.values():
            continue # raise errors.AccountHasNoEntriesError("Only Header")
        if row.get(CSVHeader.ACCOUNTID) == accountid and row.get(CSVHeader.EVENTID) == eventid:
            continue
        newCSV.append(row)

    entryfile_write = open(_CSV_ENTRY, "w", newline="")
    writer = csv.DictWriter(entryfile_write, fieldnames=CSVHeader.AsList(),
                            delimiter=",")

    writer.writerow(dict(zip(CSVHeader.AsList(), CSVHeader.AsList())))
    writer.writerows(newCSV)

