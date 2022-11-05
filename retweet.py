from tweepy import Client

from helper import CONFIG, matcher
from log import logger


def home_timeline(twitter: Client) -> None:
    if timeline := twitter.get_home_timeline(
        max_results=CONFIG["MaxResults"]["Tweets"],
        expansions=[
            "attachments.poll_ids",
            "attachments.media_keys",
            "author_id",
            "geo.place_id",
            "in_reply_to_user_id",
            "referenced_tweets.id",
            "referenced_tweets.id.author_id",
        ],
        media_fields=[
            "duration_ms",
            "height",
            "media_key",
            "preview_image_url",
            "type",
            "url",
            "width",
            "public_metrics",
            "alt_text",
            "variants",
        ],
        tweet_fields=[
            "attachments",
            "author_id",
            "context_annotations",
            "conversation_id",
            "created_at",
            "entities",
            "geo",
            "id",
            "in_reply_to_user_id",
            "lang",
            "public_metrics",
            "possibly_sensitive",
            "referenced_tweets",
            "reply_settings",
            "source",
            "text",
            "withheld",
        ],
        user_fields=[
            "created_at",
            "description",
            "entities",
            "id",
            "location",
            "name",
            "pinned_tweet_id",
            "profile_image_url",
            "protected",
            "public_metrics",
            "url",
            "username",
            "verified",
            "withheld",
        ],
        poll_fields=[
            "duration_minutes",
            "end_datetime",
            "id",
            "options",
            "voting_status",
        ],
        place_fields=[
            "contained_within",
            "country",
            "country_code",
            "full_name",
            "geo",
            "id",
            "name",
            "place_type",
        ],
    ).data:  # type: ignore
        retweeted_ids = {
            tweet.id
            for tweet in twitter.get_users_tweets(
                id=twitter.get_me().data.id,  # type: ignore
                max_results=CONFIG["MaxResults"]["Tweets"],
            ).data  # type: ignore
        }
        for tweet in timeline:
            if (
                tweet.id not in retweeted_ids
                and matcher(tweet)
                and twitter.retweet(tweet_id=tweet.id).data[  # type: ignore
                    "retweeted"
                ]
            ):
                logger.info(
                    f"retweeted success, id: {tweet.id}, text: {tweet.text}"
                )
                retweeted_ids.add(tweet.id)
