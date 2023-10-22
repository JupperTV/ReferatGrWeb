class AccountAlreadyExistsError(Exception):
    def __init__(*args):
        super().__init__("Ein Account mit der selben E-Mail ist bereits registriert", *args)
    
class EmailIsNotRegisteredError(Exception):
    def __init__(*args):
        super().__init__("Die Email ist nicht Registriert", *args)
    