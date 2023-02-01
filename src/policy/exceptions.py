class UnrecoverableError(Exception):
    pass


class EngineError(Exception):
    pass


class BrowserError(EngineError):
    pass


class ContextError(EngineError):
    pass


class PageError(EngineError):
    pass


class PageLoaded(Exception):
    pass
