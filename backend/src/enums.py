import enum


class LabeledEnum(enum.IntEnum):
    """
    Example usage:

    class MyEnum(LabeledEnum):
        OPTION = 1, "first option"

    >>> MyEnum.OPTION == 1
    True

    >>> MyEnum.OPTION.label
    first option
    """

    def __new__(
        cls: "LabeledEnum",
        value: int,
        label: str | None = None,
    ) -> "LabeledEnum":
        obj = int.__new__(cls, value)
        obj._value_ = value

        obj.label = label or ""
        return obj


class WSError(LabeledEnum):
    TOKEN_REQUIRED = 4000, "Token is required"
    INVALID_TOKEN = 4001, "Invalid token"
    TOKEN_EXPIRED = 4002, "Token has expired"
    INACTIVE_USER = 4003, "Inactive user"
    VALIDATION_ERROR = 4004, "Validation error"
