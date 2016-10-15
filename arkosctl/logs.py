import datetime
import logging


class LoggingControl:
    """Control logging for runtime events, using `logging` module API."""

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("arkosctl")
        logging.addLevelName(25, "SUCCESS")

    def add_stream_logger(
            self, st="[{levelname}] {comp}: {message}",
            debug=False):
        """Create a new stream logger."""
        self.logger.handlers = []
        stdout = logging.StreamHandler()
        self.logger.setLevel(logging.DEBUG)
        stdout.setLevel(logging.DEBUG if debug else logging.INFO)
        dformatter = StreamFormatter(st)
        stdout.setFormatter(dformatter)
        self.logger.addHandler(stdout)

    def _log(self, level, mobj, exc_info=False):
        self.logger.log(level, mobj, exc_info=exc_info)

    def debug(self, comp, message, id=None):
        """Send a message with log level DEBUG."""
        self._log(10, {
            "cls": "runtime", "comp": comp, "title": None, "message": message
        })

    def info(self, comp, message, id=None):
        """Send a message with log level INFO."""
        self._log(20, {
            "cls": "runtime", "comp": comp, "title": None, "message": message
        })

    def success(self, comp, message, id=None):
        """Send a message with log level SUCCESS."""
        self._log(25, {
            "cls": "runtime", "comp": comp, "title": None, "message": message
        })

    def warning(self, comp, message, id=None):
        """Send a message with log level WARNING."""
        self._log(30, {
            "cls": "runtime", "comp": comp, "title": None, "message": message
        })

    def error(self, comp, message, id=None):
        """Send a message with log level ERROR."""
        self._log(40, {
            "cls": "runtime", "comp": comp, "title": None, "message": message
        }, exc_info=True)

    def critical(self, comp, message, id=None):
        """Send a message with log level CRITICAL."""
        self._log(50, {
            "cls": "runtime", "comp": comp, "title": None, "message": message
        })


class StreamFormatter(logging.Formatter):
    def format(self, record):
        if type(record.msg) in [str, bytes]:
            data = {
                "title": None, "message": record.msg, "comp": "Unknown",
                "cls": "runtime"
            }
        else:
            data = record.msg.copy()
        levelname = "CRITICAL"
        logtime = datetime.datetime.fromtimestamp(record.created)
        logtime = logtime.strftime("%Y-%m-%d %H:%M:%S")
        logtime = "%s,%03d" % (logtime, record.msecs)
        if record.levelname == "DEBUG":
            levelname = "\033[37mDEBUG\033[0m  "
        if record.levelname == "INFO":
            levelname = "\033[36mINFO\033[0m   "
        if record.levelname == "SUCCESS":
            levelname = "\033[32mSUCCESS\033[0m"
        if record.levelname == "WARNING":
            levelname = "\033[33mWARN\033[0m   "
        if record.levelname == "ERROR":
            levelname = "\033[31mERROR\033[0m  "
        data.update({"cls": data["cls"].upper()[0], "levelname": levelname,
                     "asctime": logtime})
        result = self._fmt.format(**data)
        return result
