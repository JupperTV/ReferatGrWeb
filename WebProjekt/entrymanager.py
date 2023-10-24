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
        return iter([self.entryid, account.accountid, event.eventid])


_CSV_PATH: Final[str] = "data"
_CSV_ENTRY: Final[str] = f"{_CSV_PATH}\\entries.csv"

def CreateEntry(accountid: int, eventid: int):
    entryfile_write = open(_CSV_ENTRY, "a", newline="")
    writer = csv.writer(entryfile_writer, delimiter=",")
    entryid = uuid.uuid4()
    #writer.writerow(list(Entry())) # TODO
    writer.writerow(entryid, accountid, eventid)


def SendMessageToEntries(message: str, eventid: int):
    raise NotImplementedError("Sende eine Nachricht (z.B. Erinnerung) an alle Accounts, die sich zu dem Event angemeldet haben")

# Eine Entry muss, von aus logischer Sicht her, nicht modifiziert werden

def DeleteEntry(accountid: int, eventid: int):
    raise NotImplementedError("Lösche eine Zeile in entries.csv")

