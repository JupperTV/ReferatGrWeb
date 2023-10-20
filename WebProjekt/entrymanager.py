# ! TODO:

# Was ist ein Entry?
# Ein Entry ist das, was ein Account zu einem Event verbindet.
# Wenn z.B. ein Benutzer sich für ein Event einträgt, dann wird das
# als einen Eintrag bzw. einer Anmeldung zu diesem Event gespeichert
def CreateEntry(accountid: int, eventid: int):
    raise NotImplementedError("Schreibe eine Zeile in entries.csv")

def SendMessageToEntries(message: str, eventid: int):
    raise NotImplementedError("Sende eine Nachricht (z.B. Erinnerung) an alle Accounts, die sich zu dem Event angemeldet haben")

def DeleteEntry(accountid: int, eventid: int):
    raise NotImplementedError("Lösche eine Zeile in entries.csv")

