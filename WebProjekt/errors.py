class AccountAlreadyExistsError(Exception):
    def __init__(self=None):
        super().__init__("Ein Account mit der selben E-Mail ist bereits registriert")

class AccountDoesNotExistError(Exception):
    def __init__(self=None):
        super().__init__("Die Email ist nicht Registriert")

class EventAlreadyExistsError(Exception):
    def __init__(self=None):
        super().__init__("Das Event existiert bereit")

class NotEnoughElementsInListError(Exception):
    def __init__(self=None):
        super().__init__("Es gibt nicht genug Elemente in der Liste")

class AccountHasNoEntriesError(Exception):
    def __init__(self=None):
        super().__init__("Der Account hat keine Einträge für Events")

class AccountHasNoEventsError(Exception):
    def __init__(self=None):
        super().__init__("Der Account hat keine Events erstellt")
