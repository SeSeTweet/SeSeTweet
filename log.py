import logging


stream_handler = logging.StreamHandler()
stream_handler.setLevel("INFO")

file_handler = logging.FileHandler("SeSeTweet.log", errors="replace")
file_handler.setLevel("INFO")


logger = logging.getLogger("SeSeTweet")
logger.setLevel("INFO")

logger.addHandler(stream_handler)
logger.addHandler(file_handler)
