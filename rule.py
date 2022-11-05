from pathlib import Path
from typing import Any, Dict, List

import yaml

from matcher import (
    Attachment,
    AuthorID,
    ConversationID,
    CreatedAt,
    Emoji,
    Geo,
    HashTag,
    Keyword,
    Lang,
    LikeCount,
    Matcher,
    Mention,
    NullMatcher,
    QuoteCount,
    Regex,
    ReplyCount,
    RetweetCount,
    Sensitive,
    Source,
    Url,
)


def rule_parser(rules: Dict[str, Any] | None) -> Matcher:
    def typer(field: Dict[str, Any] | None) -> Matcher:
        def _typer(typed: str, value: Any) -> Matcher:
            match typed:
                case "attachment":
                    return Attachment(value)
                case "author_id":
                    return AuthorID(value)
                case "conversation_id":
                    return ConversationID(value)
                case "created_at":
                    created_at, op = value.split(",")
                    return CreatedAt(created_at, operator=op)
                case "emoji":
                    return Emoji(value)
                case "geo":
                    return Geo(value)
                case "hashtag":
                    return HashTag(value)
                case "keyword":
                    return Keyword(value)
                case "lang":
                    return Lang(value)
                case "like_count":
                    like_count, op = value.split(",")
                    return LikeCount(int(like_count), operator=op)
                case "mention":
                    return Mention(value)
                case "quote_count":
                    quote_count, op = value.split(",")
                    return QuoteCount(int(quote_count), operator=op)
                case "regex":
                    return Regex(value)
                case "reply_count":
                    reply_count, op = value.split(",")
                    return ReplyCount(int(reply_count), operator=op)
                case "retweet_count":
                    retweet_count, op = value.split(",")
                    return RetweetCount(int(retweet_count), operator=op)
                case "sensitive":
                    return Sensitive()
                case "source":
                    return Source(value)
                case "url":
                    return Url(value)
                case _:
                    return NullMatcher()

        match field:
            case {"type": t, "value": value} if t.startswith("~"):
                return ~_typer(t.removeprefix("~"), value)
            case {"type": t, "value": value}:
                return _typer(t, value)
            case _:
                return NullMatcher()

    def op_and(rules: List[Dict[str, Any]]) -> None:
        nonlocal root

        for value in rules:
            match value:
                case str():
                    root &= typer(value)
                case dict():
                    root &= rule_parser(value)

    def op_or(rules: List[Dict[str, Any]]) -> None:
        nonlocal root

        for value in rules:
            match value:
                case str():
                    root |= typer(value)
                case dict():
                    root |= rule_parser(value)

    root = NullMatcher()

    match rules:
        case {"and": and_rule, "or": or_rule}:
            op_and(and_rule)
            op_or(or_rule)
        case {"and": rule}:
            op_and(rule)
        case {"or": rule}:
            op_or(rule)
        case _:
            return typer(rules)

    return root


def rules_loader(rules: Dict[str, Any] | None) -> Matcher:
    def loader(path: str) -> Dict[str, Any]:
        return yaml.safe_load(Path(path).read_bytes())["Rule"]

    def op_and(rules: List[str | Dict[str, Any]]) -> None:
        nonlocal root

        for value in rules:
            match value:
                case str():
                    root &= rule_parser(loader(value))
                case dict():
                    root &= rules_loader(value)

    def op_or(rules: List[str | Dict[str, Any]]) -> None:
        nonlocal root

        for value in rules:
            match value:
                case str():
                    root |= rule_parser(loader(value))
                case dict():
                    root |= rules_loader(value)

    root = NullMatcher()

    match rules:
        case {"and": and_rule, "or": or_rule}:
            op_and(and_rule)
            op_or(or_rule)
        case {"and": rule}:
            op_and(rule)
        case {"or": rule}:
            op_or(rule)
        case _:
            return rule_parser(rules)

    return root
