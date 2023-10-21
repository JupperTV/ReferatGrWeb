class AccountAlreadyExists(Exception):
    def __init__(*args):
        super().__init__("Ein Account mit der selben E-Mail ist bereits registriert", *args)
    