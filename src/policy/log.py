from logging import LoggerAdapter


class CustomAdapter(LoggerAdapter):
    def process(self, msg, kwargs):
        return '[%s] %s' % (self.extra, msg), kwargs
