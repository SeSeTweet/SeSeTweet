from datetime import datetime
from operator import eq, ge, gt, le, lt, ne
from re import compile
from typing import Any, Callable, NoReturn

from dateutil.parser import parse
from tweepy.tweet import Tweet

__all__ = (
    "Attachment",
    "AuthorID",
    "ConversationID",
    "CreatedAt",
    "Emoji",
    "Geo",
    "HashTag",
    "Keyword",
    "Lang",
    "LikeCount",
    "Matcher",
    "Mention",
    "NullMatcher",
    "QuoteCount",
    "Regex",
    "ReplyCount",
    "RetweetCount",
    "Sensitive",
    "Source",
    "Url",
)


class Matcher:
    __slots__ = ("func", "_repr")

    def __init__(self, func: Callable[..., bool]):
        self.func = func

    def __call__(self, x: Any) -> bool:
        return self.func(x)

    def __and__(self, other: "Matcher") -> "Matcher":
        matcher = Matcher(lambda func: self(func) and other(func))
        matcher._repr = f"({self!r} & {other!r})"
        return matcher

    def __or__(self, other: "Matcher") -> "Matcher":
        matcher = Matcher(lambda func: self(func) or other(func))
        matcher._repr = f"({self!r} | {other!r})"
        return matcher

    def __invert__(self) -> "Matcher":
        matcher = Matcher(lambda func: not self(func))
        matcher._repr = f"~{self!r}"
        return matcher

    def __repr__(self) -> str:
        return self._repr


class NullMatcher(Matcher):
    __slots__ = ()

    def __init__(self):
        super().__init__(lambda _: True)

    def __call__(self, text: str) -> bool:
        return self.func(text)

    def __and__(self, other: Matcher) -> Matcher:
        return other

    def __or__(self, other: Matcher) -> Matcher:
        return other

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[]"


def _operator(
    op: str, *, eq=eq, ge=ge, gt=gt, le=le, lt=lt, ne=ne
) -> Callable | NoReturn:
    match op:
        case "eq" | "=":
            return eq
        case "ge" | ">=":
            return ge
        case "gt" | ">":
            return gt
        case "le" | "<=":
            return le
        case "lt" | "<":
            return lt
        case "ne" | "!=":
            return ne
        case _:
            raise NotImplementedError("unknow operator", op)


##########
# Matcher
##########
class Attachment(Matcher):
    __slots__ = ("attachment",)

    def __init__(self, attachment: str | None):
        self.attachment = attachment
        super().__init__(
            lambda tweet: self._entities_extractor(
                tweet=tweet, attachment=attachment
            )
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self .attachment}]"

    def _entities_extractor(
        self, tweet: Tweet, attachment: str | None
    ) -> bool:
        if tweet.attachments and (
            attachments := tweet.attachments.get("attachments")
        ):
            if attachment is None:
                return True

            return attachment in attachments["media_keys"]

        return False


class AuthorID(Matcher):
    __slots__ = ("author_id",)

    def __init__(self, author_id: int):
        self.author_id = author_id
        super().__init__(lambda tweet: tweet.author_id == author_id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.author_id}]"


class ConversationID(Matcher):
    __slots__ = ("conversation_id",)

    def __init__(self, conversation_id: int):
        self.conversation_id = conversation_id
        super().__init__(
            lambda tweet: tweet.conversation_id == conversation_id
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.conversation_id}]"


class CreatedAt(Matcher):
    __slots__ = ("created_at", "op")

    def __init__(
        self,
        created_at: str | datetime,
        *,
        operator="ge",
        parse=parse,
        str=str,
        operator_func=_operator,
    ):
        if isinstance(created_at, str):
            created_at = parse(created_at)

        self.created_at = created_at
        self.op = operator
        op = operator_func(operator)

        super().__init__(
            lambda tweet: op(created_at.astimezone(), tweet.created_at)
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.created_at},{self.op}]"


class Emoji(Matcher):
    __slots__ = ("emoji",)

    def __init__(self, emoji: str):
        self.emoji = emoji
        super().__init__(lambda tweet: emoji in tweet.text)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.emoji}]"


class Geo(Matcher):
    __slots__ = ("geo",)

    def __init__(self, geo: str) -> None:
        self.geo = geo
        super().__init__(lambda tweet: geo == tweet.geo)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.geo}]"


class HashTag(Matcher):
    __slots__ = ("tag",)

    def __init__(self, tag: str | None):
        self.tag = tag
        super().__init__(
            lambda tweet: self._entities_extractor(tweet=tweet, tag=tag)
        )

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.tag}]"

    def _entities_extractor(self, tweet: Tweet, tag: str | None) -> bool:
        if tweet.entities and (hashtags := tweet.entities.get("hashtags")):
            if tag is None:
                return True

            for hashtag in hashtags:
                if hashtag["tag"] == tag:
                    return True

        return False


class Keyword(Matcher):
    __slots__ = ("keyword",)

    def __init__(self, keyword: str):
        self.keyword = keyword
        super().__init__(lambda tweet: keyword in tweet.text)

    def __repr__(self):
        return f"{self.__class__.__name__}[{self.keyword}]"


class Lang(Matcher):
    __slots__ = ("lang",)

    def __init__(self, lang: str):
        self.lang = lang
        super().__init__(lambda tweet: tweet.lang == lang)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.lang}]"


class LikeCount(Matcher):
    __slots__ = ("count", "op")

    def __init__(
        self, count: int = 0, *, operator: str = "ge", operator_func=_operator
    ):
        self.count = count
        self.op = operator
        op = operator_func(operator)

        super().__init__(
            lambda tweet: op(tweet["public_metrics"]["like_count"], count)
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.count},{self.op}]"


class Mention(Matcher):
    __slots__ = ("mention",)

    def __init__(self, mention: str | None):
        self.mention = mention
        super().__init__(
            lambda tweet: self._entities_extractor(
                tweet=tweet, mention=mention
            )
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.mention}]"

    def _entities_extractor(self, tweet: Tweet, mention: str | None) -> bool:
        if tweet.entities and (mentions := tweet.entities.get("mentions")):
            if mention is None:
                return True

            for mention_ in mentions:
                if mention in (mention_["username"], mention_["id"]):
                    return True

        return False


class QuoteCount(Matcher):
    __slots__ = ("count", "op")

    def __init__(
        self, count: int = 0, *, operator: str = "ge", operator_func=_operator
    ):
        self.count = count
        self.op = operator
        op = operator_func(operator)

        super().__init__(
            lambda tweet: op(tweet["public_metrics"]["quote_count"], count)
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.count},{self.op}]"


class Regex(Matcher):
    __slots__ = ("pattern",)

    def __init__(self, pattern: str, *, bool=bool, compile=compile):
        self.pattern = pattern
        pattern_ = compile(pattern=pattern)
        super().__init__(lambda tweet: bool(pattern_.search(tweet.text)))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.pattern}]"


class ReplyCount(Matcher):
    __slots__ = ("count", "op")

    def __init__(
        self, count: int = 0, *, operator: str = "ge", operator_func=_operator
    ):
        self.count = count
        self.op = operator
        op = operator_func(operator)

        super().__init__(
            lambda tweet: op(tweet["public_metrics"]["reply_count"], count)
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.count},{self.op}]"


class RetweetCount(Matcher):
    __slots__ = ("count", "op")

    def __init__(
        self, count: int = 0, *, operator: str = "ge", operator_func=_operator
    ):
        self.count = count
        self.op = operator
        op = operator_func(operator)

        super().__init__(
            lambda tweet: op(tweet["public_metrics"]["retweet_count"], count)
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.count},{self.op}]"


class Sensitive(Matcher):
    __slots__ = ("sensitive",)

    def __init__(self):
        super().__init__(lambda tweet: tweet.possibly_sensitive)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[]"


class Source(Matcher):
    __slots__ = ("source",)

    def __init__(self, source: str):
        self.source = source
        super().__init__(lambda tweet: tweet.source == source)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.source}]"


class Url(Matcher):
    __slots__ = ("url",)

    def __init__(self, url: str | None):
        self.url = url
        super().__init__(
            lambda tweet: self._entities_extractor(tweet=tweet, url=url)
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}[{self.url}]"

    def _entities_extractor(self, tweet: Tweet, url: str | None) -> bool:
        if tweet.entities and (urls := tweet.entities.get("urls")):
            if url is None:
                return True

            for url_ in urls:
                if url in (
                    url_["url"],
                    url_["expanded_url"],
                    url_["display_url"],
                ):
                    return True

        return False
