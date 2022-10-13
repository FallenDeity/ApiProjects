import logging
import logging.handlers


class Logs:
    def __init__(self) -> None:
        self.file_logger = logging.getLogger(__name__)
        self.stream_logger = logging.getLogger(__name__)
        self.file_logger.setLevel(logging.DEBUG)
        self.stream_logger.setLevel(logging.INFO)

    def file_handler(self) -> None:
        file_handler = logging.handlers.RotatingFileHandler(
            filename="logs.log", maxBytes=1024 * 1024 * 10, backupCount=10
        )
        file_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        self.file_logger.addHandler(file_handler)

    def stream_handler(self) -> None:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        self.stream_logger.addHandler(stream_handler)

    def log(self, message: str, level: str) -> None:
        match level:
            case "debug":
                self.file_logger.debug(message)
            case "info":
                self.stream_logger.info(message)
            case "warning":
                self.stream_logger.warning(message)
            case "error":
                self.stream_logger.error(message)
            case "critical":
                self.stream_logger.critical(message)
            case _:
                raise ValueError("Invalid log level")
