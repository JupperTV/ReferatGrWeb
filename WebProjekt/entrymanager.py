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

_CSV_PATH: Final[str] = "data"
_CSV_ENTRY: Final[str] = f"{_CSV_PATH}\\entries.csv"

# Statische Variablen in einer Klasse für besserer lesbarkeit
class CSVHeader:
    ENTRYID: Final[str] = "id"
    ACCOUNTID: Final[str] = "accountid"
    EVENTID: Final[str] = "eventid"


# def _getreader_() -> Iterable[list[str]]:
#     entryfile_read = open(_CSV_ENTRY, "r", newline="")
#     return csv.reader(entryfile_read, delimiter=",")

# * Ein csv.DictReader funktioniert im Prinzip wie ein list[dict[str, str]]
def _getdictreader_() -> csv.DictReader:
    entryfile_read = open(_CSV_ENTRY, "r", newline="")
    return csv.DictReader(entryfile_read, delimiter=",")

def SaveInCSV(accountid: int, eventid: int) -> None:
    entryfile_writer = open(_CSV_ENTRY, "a", newline="")
    # writer = csv.writer(entryfile_writer, delimiter=",")
    writer = csv.DictWriter(entryfile_writer, delimiter=",")
    entryid = uuid.uuid4()  # Random uuid
    writer.writerow([entryid, accountid, eventid])

def DidAccountAlreadyEnter(accountid, eventid) -> bool:
    # reader = _getreader_()
    reader = _getdictreader_()
    # next(reader)  # Skip Header  * Nicht notwendig beim dictreader
    for row in reader:
        if not row.values():  # row is empty
            continue

        # * Wichtiges Detail:
        # Es wird row.get(...) anstatt row[...] benutzt, weil
        # row.get(...) None zurückgibt, wenn der Key, bzw. die Spalte,
        # nicht existiert.
        # Das ist wichtig, weil wenn die Spalte leer ist, oder die ganze
        # Reihe leer ist, werden die Values der Keys automatisch zu None.
        # (Pythons *eingebaute* csv Bibliothek hat Leider
        # Schwierigkeiten mit Zeilenumbrüchen (siehe Kommentar
        # "Komisches Python verhalten" in accountmanager.AddAccount))
        if row.get(CSVHeader.ACCOUNTID) == accountid and row.get(CSVHeader.EVENTID) == eventid:
            return True
    return False

def GetAllEntriedEventsOfAccount(accountid) -> list[eventmanager.Event] | None:
    events: list[eventmanager.Event] = eventmanager.GetAllEvents()
    # reader: list[list[str]] = list(_getreader_())
    reader = _getdictreader_()
    if not reader:
        return None
    entriedevents: list[eventmanager.Event] = []
    for row in reader:
        if row.values() and row.get(CSVHeader.ACCOUNTID) == accountid:
            entriedevents.append(eventmanager.GetEventFromId(CSVHeader.EVENTID))
    return entriedevents

def DeleteAllEntriesWithEvent(eventid) -> None:
    events: list[eventmanager.Event] = eventmanager.GetAllEvents()
    # reader = list(_getreader_())
    # One for reading and one for removing
    reader: csv.DictReader = _getdictreader_()
    rowsWithoutEvent: list[dict[str, str]] = []
    for row in reader:
        if not row.values():
            raise errors.AccountHasNoEntriesError()
        if row.get(CSVHeader.EVENTID) == eventid:
            continue
        rowsWithoutEvent.append(row)
    
    # ! Wichtige Notiz:
    # Die Datei wird direkt nach dem öffnen komplett gelöscht.
    # Bei writer.writerows() wird sie komplett neugeschrieben
    entryfile_write = open(_CSV_ENTRY, "w", newline="")
    # writer = csv.writer(csvfile, delimiter=",")
    writer = csv.DictWriter(entryfile_write, delimiter=",")
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

    # ! Wichtige Notiz:
    # Die Datei wird direkt nach dem öffnen komplett gelöscht.
    # Bei writer.writerows() wird sie komplett neugeschrieben
    entryfile_write = open(_CSV_ENTRY, "w", newline="")
    # Ich benutze hier einen normalen writer, weil ich das vorher in
    # eine list umgewandelt habe, weil es so für mich einfacher ist,
    # eine Zeile zu löschen
    writer = csv.DictWriter(entryfile_write, delimiter=",")
    writer.writerows(newCSV)
