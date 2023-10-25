#!/usr/bin/python
# * Was ist ein Entry?
# Ein Entry ist das, was ein Account mit einem Event verbindet.
# Wenn z.B. ein Benutzer sich für ein Event einträgt, dann wird das
# als einen Eintrag bzw. einer Anmeldung zu diesem Event gespeichert

import csv
from typing import Final, Iterable
import uuid

import accountmanager
import eventmanager
import errors

class Entry:
    def __init__(self, entryid, account: accountmanager.Account,
                event: eventmanager.Event):
        self.entryid = entryid
        self.account = account
        self.event = event

    def __iter__(self):
        return iter([self.entryid, self.account.accountid, self.event.eventid])


_CSV_PATH: Final[str] = "data"
_CSV_ENTRY: Final[str] = f"{_CSV_PATH}\\entries.csv"

def _getreader_() -> Iterable[list[str]]:
    entryfile_read = open(_CSV_ENTRY, "r", newline="")
    return csv.reader(entryfile_read, delimiter=",")

def CreateEntry(accountid: int, eventid: int) -> None:
    entryfile_writer = open(_CSV_ENTRY, "a", newline="")
    writer = csv.writer(entryfile_writer, delimiter=",")
    entryid = uuid.uuid4()  # Random uuid

    writer.writerow([entryid, accountid, eventid])

def DidAccountAlreadyEnter(accountid, eventid) -> bool:
    reader = _getreader_()
    next(reader)  # Skip Header
    for row in reader:
        if not row:  # row is empty
            continue
        if row[1] == accountid and row[2] == eventid:
            return True
    return False

def GetAllEntriedEventsOfAccount(accountid) -> list[eventmanager.Event] | None:
    events: list[eventmanager.Event] = eventmanager.GetAllEvents()
    reader: list[list[str]] = list(_getreader_())
    if not reader[1:]:
        return None
    entriedevents: list[eventmanager.Event] = []
    for row in reader[1:]:
        if row and row[1] == accountid:
            entriedevents.append(eventmanager.GetEventFromId(row[2]))
    return entriedevents

def DeleteAllEntriesWithEvent(eventid) -> None:
    events: list[eventmanager.Event] = eventmanager.GetAllEvents()
    reader = list(_getreader_())
    rowstoremove: list[list[str]] = []
    if not reader[1:]:  # CSV enthält nur Header
        raise erros.AccountHasNoEntriesError()
    for row in reader[1:]:
        if row[2] == eventid:
            rowstoremove.append(row)
    for row in rowstoremove:
        reader.remove(row)
    # ! Important Note: The file will be completely deleted after this
    # ! The fille will be completely rewriten
    csvfile = open(_CSV_ENTRY, "w", newline="")
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerows(reader)

def DeleteEntry(accountid: int, eventid: int) -> None:
    reader = list(_getreader_())
    rowtoremove: list[str] = []
    if not reader[1:]:
        raise erros.AccountHasNoEntriesError("Nur Header")
    for row in reader[1:]:
        if row[1] == accountid and row[2] == eventid:
            rowtoremove = row
            break
    reader.remove(rowtoremove)
    # ! Important Note: The file will be completely deleted after this
    # ! We will completely rewrite it
    csvfile = open(_CSV_ENTRY, "w", newline="")
    writer = csv.writer(csvfile, delimiter=",")
    writer.writerows(reader)

