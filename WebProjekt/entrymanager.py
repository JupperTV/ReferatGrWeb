#!/usr/bin/python
# * Was ist ein Entry?
# Ein Entry ist das, was ein Account mit einem Event verbindet.
# Wenn z.B. ein Benutzer sich für ein Event einträgt, dann wird das
# als einen Eintrag bzw. einer Anmeldung zu diesem Event gespeichert

import csv
from typing import Final, Iterable
import uuid

import eventmanager
import errors

_CSV_PATH: Final[str] = "data"
_CSV_ENTRY: Final[str] = f"{_CSV_PATH}\\entries.csv"

# * Notiz:
# * Ich habe keine Klasse für die Einträge (bzw. Entries) gemacht,
# * Weil die Werte der CSV Datei sowieso nur die IDs sind

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
    # Ein Dictwriter lohnt sich nicht, weil ich beim schreiben die 3 Variablen
    # dann mit CSVHeader.AsList() zippen muss und das ist zu viel Arbeit
    writer = csv.writer(entryfile_writer, delimiter=",")
    entryid = uuid.uuid4()
    writer.writerow([entryid, accountid, eventid])

def DidAccountAlreadyEnter(accountid, eventid) -> bool:
    reader = _getdictreader_()
    for row in reader:
        if not row.values():  # row ist leer
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
            raise errors.AccountHasNoEntriesError()
        if row.get(CSVHeader.EVENTID) == eventid:
            continue
        rowsWithoutEvent.append(row)
    
    # * Wichtige Notiz:
    # Die Datei wird direkt nach dem öffnen komplett gelöscht.
    # Bei writer.writerows() wird sie komplett neugeschrieben
    with open(_CSV_ENTRY, "w", newline="") as entryfile_write:
        writer = csv.DictWriter(entryfile_write, fieldnames=CSVHeader.AsList(),
                                delimiter=",")
        writer.writerows(rowsWithoutEvent)

def DeleteEntry(accountid: int, eventid: int) -> None:
    reader = _getdictreader_()
    newCSV: list[dict[str, str]] = []
    for row in reader:
        if not row.values():
            continue # raise errors.AccountHasNoEntriesError("Nur Header")
        if row.get(CSVHeader.ACCOUNTID) == accountid and row.get(CSVHeader.EVENTID) == eventid:
            continue
        newCSV.append(row)

    with open(_CSV_ENTRY, "w", newline="") as entryfile_write:
        writer = csv.DictWriter(entryfile_write, fieldnames=CSVHeader.AsList(),
                                delimiter=",")
        writer.writerows(newCSV)
