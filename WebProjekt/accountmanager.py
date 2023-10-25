#!/usr/bin/python

# ! WICHTIGE NOTIZ: Ich obfuskiere Daten anstatt sie zu verschlüsseln,
# ! weil diese Applikation sowieso nur für Demonstrationszwecke
# ! gemacht wurde
from base64 import b64encode, b64decode  # Zum Obfuskieren der Daten
import csv  # Alle Daten werden als CSVs gespeichert
import re#gex
from typing import Final, Iterable
import uuid  # Zur Erstellung von eindeutigen IDs

import errors

# Quelle: https://regexr.com/3e48o
_REGEX_VALID_EMAIL: Final = r"^\S+@\S+\.\S+$"
_UNSUCCESFUL_MATCH = None
_CSV_PATH: Final[str] = "data"
_CSV_ACCOUNT: Final[str] = f"{_CSV_PATH}\\accounts.csv"


class Account:
    def __init__(self, accountid: str, email: str, base64password: str,
                 firstname: str, lastname: str):
        self.accountid = accountid
        self.email = email
        self.password = base64password
        self.firstname = firstname
        self.lastname = lastname

class CSVHeader:
    ACCOUNTID: Final[str] = "id"
    EMAIL: Final[str] = "email"
    PASSWORD: Final[str] = "password"
    FIRSTNAME: Final[str] = "firstname"
    LASTNAME: Final[str] = "lastname"


def _getdictreader_():
    pass

def _obfuscateText_(text: bytes) -> bytes:
    if type(text) is str:
        # Unicode anstatt UTF-8, weil Python 3 Unicode für strings benutzt
        text = bytes(text, encoding="unicode")
    return b64encode(text)

# TODO: Test
def GetFullNameOfAccount(email: str):
    accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    reader: Iterable[dict] = csv.reader(accountfile_read, delimiter=",")
    for row in reader:
        if row[1] == email:
            return f"{row[3]} {row[4]}"

# TODO: Test
# * id in accounts.csv == token im cookie
def GetUserToken(email: str) -> bool:
    # accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    # reader: list[list] = csv.reader(accountfile_read, delimiter=",")
    reader = _getdictreader_()
    for row in reader:
        if not row:  # if row is empty go to the next line
            continue
        if row[1] == email:
            return row[0]
    raise errors.EmailIsNotRegisteredError()

# TODO: Test
def GetEmailFromToken(token: str) -> str | None:
    # accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    # reader: list[dict] = list(csv.DictReader(accountfile_read, delimiter=","))
    reader = _getdictreader_()
    for row in reader:
        if row["id"] == token:
            return row["email"]
    return None

# TODO: Test
def LoginIsValid(email: str, originalpassword: str) -> bool:
    # accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    # reader: Iterable[dict] = csv.DictReader(accountfile_read, delimiter=",")
    reader = _getdictreader_()
    for row in reader:
        # Don't check passwords until emails are the same
        if row["email"] != email:
            continue
        if PasswordsAreEqual(originalpassword, row["password"]):
            return True
    return False

def PasswordsAreEqual(originalpassword: str, obfuscatedpassword: str) -> bool:
    return originalpassword == b64decode(obfuscatedpassword).decode()

# TODO: Test
def UserExists(email: str) -> bool:
    # reader = csv.reader(open(_CSV_ACCOUNT, "r"), delimiter=",")
    reader = _getdictreader_()
    for row in reader:
        if email in row:
            return True
    return False

# TODO: In Zukunft noch verbessern?
def PasswordIsValid(password: str) -> bool:
    if not password:
        return False
    return True

def EmailIsValid(email: str) -> bool:
    return re.fullmatch(_REGEX_VALID_EMAIL, email) != _UNSUCCESFUL_MATCH

# TODO: Test
# def SaveInCSV(email: str, password: str, firstname: str, lastname: str) -> None:
def SaveInCSV(account: Account) -> None:
    if not PasswordIsValid(account.password):
        raise ValueError("Password ist nicht gültig")
    if not EmailIsValid(account.email):
        raise ValueError("E-Mail Adresse ist nicht gültig")

    # * Komisches Python verhalten:
    # newline in open() ist ein leerer string, weil csv.writer
    # Zeilenumbrüche selber kontrolliert und deswegen \r\n direkt in
    # die Datei selber reinschreibt.
    # Wenn newline nicht leer ist, wird Windows jedes \r\n, dass von
    # csv.writer geschrieben wurde, zu einem \r\r\n umwandeln,
    # was bedeutet, dass eine leere Zeile zwischen jedem Datensatz
    # stehen würde.
    # Quellen:
    # - https://stackoverflow.com/a/3348664
    # - Fußnote in https://docs.python.org/3/library/csv.html?highlight=csv.writer#id3
    # accountfile_read = open(_CSV_ACCOUNT, "r", newline='')
    # reader: csv._reader = csv.reader(accountfile_read, delimiter=",")
    reader = _getdictreader_()

    for row in reader:
        if account.email in row.get(CSVHeader.EMAIL):
            raise errors.AccountAlreadyExistsError()

    accountid = uuid.uuid4()  # Zufällige UUID
    accountfile_write = open(_CSV_ACCOUNT, "a", newline='')
    writer = csv.DictWriter(accountfile_write, delimiter=",")
    passwordToSave = _obfuscateText_(bytes(account.password, "unicode_escape")).decode()
    writer.writerow([accountid, account.email, passwordToSave, account.firstname, account.lastname])
    accountfile_write.close()

# TODO
def RemoveAccount():
    pass
