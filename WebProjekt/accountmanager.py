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

__all__ = ["PasswordsAreEqual", "AddRegistration", "UserExists", "LoginIsValid",
           "EmailIsValid", "PasswordIsValid"]

class Account:
    def __init__(accountid, email, base64password,
                 firstname, lastname):
        """Alle Parameter sind vom Typ int"""
        raise NotImplementedError()

def _obfuscateText_(text: bytes) -> bytes:
    if type(text) is str:
        # Unicode anstatt UTF-8, weil Python 3 Unicode für strings benutzt
        text = bytes(text, encoding="unicode")
    return b64encode(text)

def _getreader_() -> Iterable[list[str]]:
    return NotImplementedError()

# * id in accounts.csv == token in cookie
def GetUserToken(email: str) -> bool:
    accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    reader: list[list] = list(csv.reader(accountfile_read, delimiter=","))
    for row in reader[1:]:
        if not row:  # if row is empty go to the next line
            continue
        if row[1] == email:
            accountfile_read.close()
            return row[0]
    accountfile_read.close()
    raise errors.EmailIsNotRegisteredError()

def GetEmailFromToken(token: str) -> str | None:
    accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    reader: list[dict] = list(csv.DictReader(accountfile_read, delimiter=","))
    for row in reader:
        if row["id"] == token:
            accountfile_read.close()
            return row["email"]
    accountfile_read.close()
    return None


def LoginIsValid(email: str, originalpassword: str) -> bool:
    accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    reader: Iterable[dict] = csv.DictReader(accountfile_read, delimiter=",")
    for row in reader:
        # Don't check passwords until emails are the same
        if row["email"] != email:
            continue
        if PasswordsAreEqual(originalpassword, row["password"]):
            accountfile_read.close()
            return True
    accountfile_read.close()
    return False

def PasswordsAreEqual(originalpassword: str, obfuscatedpassword: str) -> bool:
    return originalpassword == b64decode(obfuscatedpassword).decode()

def UserExists(email: str) -> bool:
    reader = csv.reader(open(_CSV_ACCOUNT, "r"), delimiter=",")
    # Skip first line because it's just headers
    for line in list(reader)[1:]:
        if email in line:
            return True
    return False

def PasswordIsValid(password: str) -> bool:
    if not password:
        return False
    return True

def EmailIsValid(email: str) -> bool:
    emailmatch: re.Match = re.fullmatch(_REGEX_VALID_EMAIL, email)
    if emailmatch == _UNSUCCESFUL_MATCH:
        return False
    return True


def AddRegistration(email: str, password: str,
                    firstname: str, lastname: str) -> None:
    if None in [email, password, firstname, lastname]:
        raise ValueError("Einer der Parameter ist `None`")
    if not firstname:
        raise ValueError("Der Vorname ist nicht gültig")
    if not lastname:
        raise ValueError("Der Nachname ist nicht gültig")
    if not PasswordIsValid(password):
        raise ValueError("Password ist nicht gültig")
    if not EmailIsValid(email):
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
    # - https://docs.python.org/3/library/csv.html?highlight=csv.writer#id3
    accountfile_read = open(_CSV_ACCOUNT, "r", newline='')
    reader: csv._reader = csv.reader(accountfile_read, delimiter=",")

    for row in reader:
        if email in row:
            raise errors.AccountAlreadyExistsError()
    accountfile_read.close()

    accountid = uuid.uuid4()  # Zufällige UUID
    accountfile_write = open(_CSV_ACCOUNT, "a", newline='')
    writer = csv.writer(accountfile_write, delimiter=",")
    passwordToSave = _obfuscateText_(bytes(password,"unicode_escape")).decode()
    writer.writerow([accountid, email, passwordToSave, firstname, lastname])
    accountfile_write.close()
