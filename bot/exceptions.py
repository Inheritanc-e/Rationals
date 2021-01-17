class AlreadyThere(Exception):
    pass


class NotThere(Exception):
    pass


class DbNotConfigured(RuntimeError):
    pass


class TableNotConfigured(RuntimeError):
    pass


class SchemaError(Exception):
    pass


class EmptyPagination(Exception):
    def __str__(self) -> str:
        return "No lines to paginate."
