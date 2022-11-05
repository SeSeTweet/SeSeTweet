import os

import tweepy
from helper import CONFIG
from log import logger
from retweet import home_timeline


def SeSeTweet() -> None:
    twitter = tweepy.Client(
        bearer_token=os.getenv("BEARER_TOKEN", CONFIG["BEARER_TOKEN"]),
        consumer_key=os.getenv("CONSUMER_KEY", CONFIG["CONSUMER_KEY"]),
        consumer_secret=os.getenv(
            "CONSUMER_SECRET", CONFIG["CONSUMER_SECRET"]
        ),
        access_token=os.getenv("ACCESS_TOKEN", CONFIG["ACCESS_TOKEN"]),
        access_token_secret=os.getenv(
            "ACCESS_TOKEN_SECRET", CONFIG["ACCESS_TOKEN_SECRET"]
        ),
        wait_on_rate_limit=CONFIG["WaitOnRateLimit"],
    )

    me = twitter.get_me().data  # type: ignore

    logger.info(
        "Login "
        f"UserId {me.id} "
        f"UserName @{me.username} "
        f"NickName {me.name}"
    )

    home_timeline(twitter)


if __name__ == "__main__":
    SeSeTweet()
