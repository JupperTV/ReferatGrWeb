#!/usr/bin/python

# ! IMPORTANT NOTE: I obfuscate the data instead of doing any encryption
# ! because this application was only created for demonstration purposes
from base64 import b64encode, b64decode  # Zum Obfuskieren der Daten
import csv  # All of the data is stored in CSV files
import re#gex
from typing import Final, Iterable
import uuid  # To create unique ids

import errors

# Source: https://regexr.com/3e48o
_REGEX_VALID_EMAIL: Final = r"^\S+@\S+\.\S+$"
_UNSUCCESFUL_MATCH = None
_CSV_PATH: Final[str] = "data"
_CSV_ACCOUNT: Final[str] = f"{_CSV_PATH}\\accounts.csv"

# Static variables inside a class for better readabilty
class CSVHeader:
    ACCOUNTID: Final[str] = "id"
    EMAIL: Final[str] = "email"
    BASE64PASSWORD: Final[str] = "password"
    FIRSTNAME: Final[str] = "firstname"
    LASTNAME: Final[str] = "lastname"
    def AsList() -> list[str]:
        return [CSVHeader.ACCOUNTID, CSVHeader.EMAIL, CSVHeader.BASE64PASSWORD,
                     CSVHeader.FIRSTNAME, CSVHeader.LASTNAME]

# A class so that, as long as app.py and eventmanager.py get the
# accountid and email from GetAccountFromEmail() or
# GetAccountFromToken(), they can get whatever account values they need
# themselves
class Account:
    def InitFromDict(dictionary: csv.DictReader | dict[str, str]):
        if len(dictionary) < 5:
            raise errors.NotEnoughElementsInListError()
        d = lambda h: dictionary.get(h)  # Less boilerplate
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


# region Private functions
# A csv.DictReader basically works like a list[dict[str, str]]
def _getdictreader_() -> csv.DictReader:
    # * FUTURE ME: I believe I wasted 5 hours on this
    # * Weird Python behaviour:
    # The newline parameter in open() is an empty string because
    # csv.writer and csv.reader have their own ways of controlling line
    # breaks (they just embed a "\r\n" by themselves)
    # If the newline parameter is not empty, Windows will turn the
    # "\r\n" that was written by csv.writer into "\r\r\n", which results
    # in an empty line between every data set.
    # Sources:
    # - https://stackoverflow.com/a/3348664
    # - Footnote in https://docs.python.org/3/library/csv.html?highlight=csv.writer#id3
    accountfile_read = open(_CSV_ACCOUNT, "r", newline="")
    return csv.DictReader(accountfile_read, delimiter=",")

def _obfuscateText_(text: bytes) -> bytes:
    if type(text) is str:
        # Unicode instead of UTF-8 because Python 3 uses unicode for
        # strings
        text = bytes(text, encoding="unicode")
    return b64encode(text)
# endregion

# * Note:
# I return an entire instance of Account so that app.py and
# entrymanager.py can get the values they need themselves without me
# always having to create a new function that just returns the value
# that is currently needed.
def GetAccountFromEmail(email: str) -> Account | None:
    reader: csv.DictReader = list(_getdictreader_())
    account = None
    for row in reader:
        # * Important Detail:
        # row.get(...) is being used instead of row[...] because
        # row.get(...) returns `None` if the key, or column, doesn't
        # exist.
        # This is important because the values of the keys will
        # automatically be None if the key/column or even
        # the entire row empty is.
        # (Python's *BUILT-IN* csv library has some unfortunate
        # differences when dealing with line breaks - see comment
        # "Weird Python behaviour" in accountmanager.AddAccount)
        if row.get(CSVHeader.EMAIL) == email:
            return Account.InitFromDict(row)
    raise errors.AccountDoesNotExistError()

# Note: accountid == token stored in the cookie
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

# TODO: Improve in the future?
def PasswordIsValid(originalpassword: str) -> bool:
    if not originalpassword:
        return False
    return True

# The HTML type "email" does everything for me
def EmailIsValid(email: str) -> bool:
    # return re.fullmatch(_REGEX_VALID_EMAIL, email) != _UNSUCCESFUL_MATCH
    return True

def SaveInCSV(email, originalpassword, firstname, lastname) -> None:
    if not PasswordIsValid(originalpassword):
        raise ValueError("Invalid password ")
    if not EmailIsValid(email):
        raise ValueError("Invalid e-mail")
    reader = _getdictreader_()

    for row in reader:
        if email == row.get(CSVHeader.EMAIL):
            raise errors.AccountAlreadyExistsError()

    accountid = uuid.uuid4()  # Random UUID
    with open(_CSV_ACCOUNT, "a", newline='') as accountfile_write:
        writer = csv.DictWriter(accountfile_write, fieldnames=CSVHeader.AsList(),
                                delimiter=",")
        # .decode() comes from the bytes class and turns the bytes
        # object into a str
        passwordToSave = _obfuscateText_(
            bytes(originalpassword, "unicode_escape")).decode()

        # There could be a better way to save the values from the
        # Account object
        values = [accountid, email, passwordToSave, firstname, lastname]
        writer.writerow(dict(zip(CSVHeader.AsList(), values)))

# TODO
def RemoveAccount():
    pass
