class ConfigError(Exception):
    pass


class ApiError(Exception):
    pass


class HathorCoreUnknownToken(Exception):
    pass


class HathorCoreMalformedToken(Exception):
    pass


class HathorCoreTimeout(Exception):
    pass


class EventValidationError(Exception):
    pass


class RdsError(Exception):
    pass


class RdsNotFoundError(RdsError):
    pass
