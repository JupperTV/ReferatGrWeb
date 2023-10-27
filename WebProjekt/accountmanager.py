#!/usr/bin/python

# ! WICHTIGE NOTIZ: Ich obfuskiere Daten anstatt sie zu verschlüsseln,
# ! weil diese Applikation sowieso nur für Demonstrationszwecke
# ! gemacht wurde
from base64 import b64encode, b64decode  # Zum Obfuskieren der Daten
import csv  # Alle Daten werden als CSVs gespeichert
import re#gex
from typing import Final, Iterable
import uuid  # Zur Erstellung von einmaligen IDs

import errors

# Quelle: https://regexr.com/3e48o
_REGEX_VALID_EMAIL: Final = r"^\S+@\S+\.\S+$"
_UNSUCCESFUL_MATCH = None
_CSV_PATH: Final[str] = "data"
_CSV_ACCOUNT: Final[str] = f"{_CSV_PATH}\\accounts.csv"

# Statische Variablen in einer Klasse für bessere lesbarkeit
class CSVHeader:
    ACCOUNTID: Final[str] = "id"
    EMAIL: Final[str] = "email"
    BASE64PASSWORD: Final[str] = "password"
    FIRSTNAME: Final[str] = "firstname"
    LASTNAME: Final[str] = "lastname"
    def AsList() -> list[str]:
        return [CSVHeader.ACCOUNTID, CSVHeader.EMAIL, CSVHeader.BASE64PASSWORD,
                     CSVHeader.FIRSTNAME, CSVHeader.LASTNAME]

# Eine Klasse, damit sich app.py und eventmanager.py die Werte selber
# nehmen können, solange sie die accountid oder email in
# GetAccountFromEmail() oder GetAccountFromToken() selber holen
class Account:
    def InitFromDict(dictionary: csv.DictReader | dict[str, str]):
        if len(dictionary) < 5:
            raise errors.NotEnoughElementsInListError()
        d = lambda h: dictionary.get(h)  # Weniger Boilerplate
        return Account(
            accountid=d(CSVHeader.ACCOUNTID), email=d(CSVHeader.EMAIL),
            base64password=d(CSVHeader.BASE64PASSWORD),
            firstname=d(CSVHeader.FIRSTNAME), lastname=d(CSVHeader.LASTNAME))


    def __init__(self, accountid: str, email: str, base64password: str,
                 firstname: str, lastname: str):
        self.accountid = accountid
        self.email = email
        self.base64password = base64password
        self.firstname = firstname
        self.lastname = lastname


# region Private Funktionen
# Ein csv.DictReader funktioniert im Prinzip wie ein list[dict[str, str]]
def _getdictreader_() -> csv.DictReader:
    # * Komisches Python verhalten:
    # newline in open() ist ein leerer string, weil csv.writer
    # und csv.reader Zeilenumbrüche selber kontrollieren und deswegen
    # \r\n direkt in die Datei selber reinschreiben.
    # Wenn newline nicht leer ist, wird Windows jedes \r\n, dass von
    # csv.writer geschrieben wurde, in \r\r\n umwandeln,
    # was bedeutet, dass eine leere Zeile zwischen jedem Datensatz
    # stehen würde.
    # Quellen:
    # - https://stackoverflow.com/a/3348664
    # - Fußnote in https://docs.python.org/3/library/csv.html?highlight=csv.writer#id3
    accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    return csv.DictReader(accountfile_read, delimiter=",")

def _obfuscateText_(text: bytes) -> bytes:
    if type(text) is str:
        # Unicode anstatt UTF-8, weil Python 3 Unicode für strings benutzt
        text = bytes(text, encoding="unicode")
    return b64encode(text)
# endregion

# *Notiz:
# Ich gebe eine ganzes Objekt von Account zurück, damit app.py und
# entrymanager.py sich die Werte nehmen können, die sie brauchen,
# ohne, dass ich jedesmal eine neue Funktion machen muss, wo ich nur
# den Wert, der gerade gebraucht wird, ausgeben
def GetAccountFromEmail(email: str) -> Account | None:
    reader: csv.DictReader = list(_getdictreader_())
    account = None
    for row in reader:
        # * Wichtiges Detail:
        # Es wird row.get(...) anstatt row[...] benutzt, weil
        # row.get(...) None zurückgibt, wenn der Key, bzw. die Spalte,
        # nicht existiert.
        # Das ist wichtig, weil wenn die Spalte leer ist, oder die ganze
        # Reihe leer ist, werden die Values der Keys automatisch zu None.
        # (Pythons *eingebaute* csv Bibliothek hat Leider
        # Schwierigkeiten mit Zeilenumbrüchen (siehe Kommentar
        # "Komisches Python verhalten" in accountmanager.AddAccount))
        if row.get(CSVHeader.EMAIL) == email:
            return Account.InitFromDict(row)
    raise errors.AccountDoesNotExistError()

# Notiz: Accountid == Token im Cookie
def GetAccountFromToken(token: str) -> Account:
    reader: csv.DictReader = _getdictreader_()
    for row in reader:
        if row.get(CSVHeader.ACCOUNTID) == token:
            return Account.InitFromDict(row)

def PasswordsAreEqual(originalpassword: str, obfuscatedpassword: str) -> bool:
    return originalpassword == b64decode(obfuscatedpassword).decode()

def LoginIsValid(email: str, originalpassword: str) -> bool:
    # accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    # reader: Iterable[dict] = csv.DictReader(accountfile_read, delimiter=",")
    reader: csv.DictReader = _getdictreader_()
    for row in reader:
        # Don't check passwords until emails are the same
        if row.get(CSVHeader.EMAIL) != email:
            continue
        if PasswordsAreEqual(originalpassword=originalpassword,
                             obfuscatedpassword=row.get(CSVHeader.BASE64PASSWORD)):
            return True
    return False

# TODO: Test
def UserExists(email: str) -> bool:
    reader = _getdictreader_()
    for row in reader:
        if row.get(CSVHeader.EMAIL) == email:
            return True
    return False

# TODO: In Zukunft noch verbessern?
def PasswordIsValid(originalpassword: str) -> bool:
    if not originalpassword:
        return False
    return True

def EmailIsValid(email: str) -> bool:
    return re.fullmatch(_REGEX_VALID_EMAIL, email) != _UNSUCCESFUL_MATCH

def SaveInCSV(email, originalpassword, firstname, lastname) -> None:
    if not PasswordIsValid(originalpassword):
        raise ValueError("Password ist nicht gültig")
    if not EmailIsValid(email):
        raise ValueError("E-Mail Adresse ist nicht gültig")
    reader = _getdictreader_()

    for row in reader:
        if email == row.get(CSVHeader.EMAIL):
            raise errors.AccountAlreadyExistsError()

    accountid = uuid.uuid4()  # Zufällige UUID
    with open(_CSV_ACCOUNT, "a", newline='') as accountfile_write:
        writer = csv.DictWriter(accountfile_write, fieldnames=CSVHeader.AsList(),
                                delimiter=",")
        # .decode() ist von der bytes Klasse und wandelt das bytes Objekt
        # in einen str um
        passwordToSave = _obfuscateText_(
            bytes(originalpassword, "unicode_escape")).decode()

        # Es kann sein, dass es einen besseren Weg gibt, die Werte aus
        # dem Account Objekt zu speichern
        writer.writerow([accountid, email, passwordToSave,
                         firstname, lastname])

# TODO
def RemoveAccount():
    pass
