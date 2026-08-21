class ProductctlError(Exception):
    category = "internal"

    def __init__(self, message: str, category: str | None = None) -> None:
        super().__init__(message)
        if category:
            self.category = category
        self.message = message


class UsageError(ProductctlError):
    category = "usage"


class MutationDenied(ProductctlError):
    category = "mutation_denied"


class ContractError(ProductctlError):
    pass


class InvalidContract(ContractError):
    category = "invalid_contract"


class IncompleteContract(ContractError):
    category = "incomplete_contract"


class UnconfirmedContract(ContractError):
    category = "unconfirmed_contract"
