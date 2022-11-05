import socket
from pathlib import Path

import socks
import yaml
from rule import rule_parser, rules_loader

CONFIG = yaml.safe_load(Path("SeSeTweet.yml").read_bytes())


if (host := CONFIG["Proxy"]["Host"]) and (port := CONFIG["Proxy"]["Port"]):
    socks.set_default_proxy(socks.SOCKS5, host, int(port))
    socket.socket = socks.socksocket

matcher = (
    rules_loader(CONFIG["Rules"])
    if CONFIG["Rules"]
    else rule_parser(CONFIG["Rule"])
)
