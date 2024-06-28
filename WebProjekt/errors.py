class AccountAlreadyExistsError(Exception):
    def __init__(self=None):
        super().__init__("An account with the same e-mail is already registered")

class AccountDoesNotExistError(Exception):
    def __init__(self=None):
        super().__init__("The e-mail is not registered")

class EventAlreadyExistsError(Exception):
    def __init__(self=None):
        super().__init__("The event already exists")

class NotEnoughElementsInListError(Exception):
    def __init__(self=None):
        super().__init__("There are not enough elements in the list")

class AccountHasNoEntriesError(Exception):
    def __init__(self=None):
        super().__init__("The account doesn't have any entries for the event")

class AccountHasNoEventsError(Exception):
    def __init__(self=None):
        super().__init__("Der Account hat keine Events erstellt")
