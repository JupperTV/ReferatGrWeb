class AccountAlreadyExistsError(Exception):
    def __init__(*args):
        super().__init__("Ein Account mit der selben E-Mail ist bereits registriert", *args)

class EmailIsNotRegisteredError(Exception):
    def __init__(*args):
        super().__init__("Die Email ist nicht Registriert", *args)

class EventAlreadyExistsError(Exception):
    def __init__(*args):
        super().__init__("Das Event existiert bereit", *args)

class NotEnoughElementsInListError(Exception):
    def __init__(*args):
        super().__init__("Es gibt nicht genug Elemente in der Liste", *args)

