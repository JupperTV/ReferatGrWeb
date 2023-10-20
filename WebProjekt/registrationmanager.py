#!/usr/bin/python
# Obwohl ich Windows benutze, ist hier ein Shebang zur Sicherheit

import csv  # Alle Daten werden als CSVs gespeichert
import _io
from typing import Final
import re  # Regex

# * WICHTIGE NOTIZ: Ich obfuskiere Daten, anstatt sie zu verschlüsseln,
# * weil diese Applikation sowieso nur für Demonstrationszwecke
# * gemacht wurde
from base64 import b64encode, b64decode  # Zum Obfuskieren der Daten
import pathlib  # Possible usage in the future
import uuid  # Zur Erstellung von eindeutigen IDs

# Quelle: https://regexr.com/3e48o
REGEX_VALID_EMAIL: Final = "^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$"
UNSUCCESFUL_MATCH = None

PATH_TO_CSV_FILES: Final[str] = "data"
PATH_TO_ACCOUNT_CSV = Final[str] = f"{PATH_TO_CSV_FILES}\\accounts.csv"
PATH_TO_EVENT_CSV = Final[str] = f"{PATH_TO_CSV_FILES}\\events.csv"
PATH_TO_ENTRIES_CSV = Final[str] = f"{PATH_TO_CSV_FILES}\\entries.csv"


def ObfuscatePassword(password: bytes) -> bytes:
    if type(password) is str:
        # Unicode anstatt UTF-8, weil Python 3 Unicode für strings benutzt
        password = bytes(password, encoding="unicode")
    return b64encode(password)


def CheckPassword(obfuscatedpassword: bytes, originalpassword: str) -> bool:
    if type(originalpassword) is str:
        # Unicode anstatt UTF-8, weil Python 3 Unicode für strings benutzt
        originalpassword = bytes(originalpassword, encoding="unicode")
    return b64decode(obfuscatedpassword) == originalpassword


def AddRegistration(email: str, originalpassword: str,
                    firstname: str, lastname: str):
    if None in [email, encryptedpassword, firstname, lastname]:
        raise ValueError("Einer der Parameter ist `None`")
    emailmatch: re.Match = re.fullmatch(REGEX_VALID_EMAIL, email)
    if emailmatch == UNSUCCESFUL_MATCH:
        raise ValueError("Invalide E-Mail Adresse")
    if not firstname:
        raise ValueError("Der Vorname ist nicht gültig")
    if not lastname:
        raise ValueError("Der Nachname ist nicht gültig")

    accountid = uuid.uuid4()  # Zufällige UUID
    accountsCSV: _io.TextIOWrapper = open(f"{PATH_TO_CSV_FILES}\\accounts.csv")
    CSVWriter = csv.writer(accountsCSV, delimiter=",")
    passwordToSave = ObfuscatePassword(bytes(originalpassword, "unicode"))
    CSVWriter.writerow([accountid, email, passwordToSave, firstname, lastname])

