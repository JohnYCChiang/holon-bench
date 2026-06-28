import re


def translate(pattern):
    regex = pattern.replace("*", ".*").replace("?", ".")
    return "^" + regex + "$"


def matches(pattern, name):
    return re.match(translate(pattern), name) is not None
