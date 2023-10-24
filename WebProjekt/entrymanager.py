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

def _getreader_() -> csv._reader:
    entryfile_read = open(_CSV_ENTRY, "r", newline="")
    return csv.reader(entryfile_read, delimiter=",")

def CreateEntry(accountid: int, eventid: int) -> None:
    entryfile_writer = open(_CSV_ENTRY, "a", newline="")
    writer = csv.writer(entryfile_writer, delimiter=",")
    entryid = uuid.uuid4()  # Random uuid
    #writer.writerow(list(Entry())) # TODO
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

def GetAllEntriedEventsOfAccount(accountid):
    events: list[eventmanager.Event] = eventmanager.GetAllEvents()
    reader: csv._reader = _getreader_()
    next(reader)  # Skip Header
    entriedevents: list = []
    for row in reader:
        if row[1] == accountid:
            entriedevents.append(eventmanager.GetEventFromId(row[2]))
        pass
    return NotImplementedError()

def SendMessageToEntries(message: str, eventid: int):
    raise NotImplementedError("Sende eine Nachricht (z.B. Erinnerung) an alle Accounts, die sich zu dem Event angemeldet haben")

# Eine Entry muss, von aus logischer Sicht her, nicht modifiziert werden

def DeleteEntry(accountid: int, eventid: int):
    raise NotImplementedError("Lösche eine Zeile in entries.csv")

