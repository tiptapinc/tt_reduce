#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2014 tiptap. All rights reserved.

clean text before running through the LIWCAlike analyzer

"""
# use regex module instead of re because re does not support
# lookbehind with variable-width pattern
import regex

# lookbehind & lookahead regex additions that are prepended and
# appended to the substitution patters
LB = "(?<=\s|^)("
LA = ")(?=\s|$)"


UNICODE_TRANS_TAB = {
    ord(u'\u2013'): u'-',
    ord(u'\u2018'): u'\'',
    ord(u'\u2019'): u'\'',
    ord(u'\u201c'): u'\"',
    ord(u'\u201d'): u'\"',
}


def translate_unicodes(text):
    return text.translate(UNICODE_TRANS_TAB)


LINKS_REGEXP = r"\b((http:|https:)\/\/[\S]*)\b"
LINKS_REPLACEMENT = "xylink"


def replace_links(text):
    prog = regex.compile(LINKS_REGEXP)
    return prog.sub(LINKS_REPLACEMENT, text)


SMILE = [
    ":)",
    ": )",
    ":-)",
    ": - )",
    ": ]",
    ": 3",
    ": c )",
    ": >",
    "= ]",
    "8 )",
    "= )",
    ": }",
    ": - D",
    ": D",
    "8 - D",
    "8D",
    "xD",
    ": - ) )",
    ";-)",
    "; - )",
    ";)",
    "; )",
    "; ]",
    "; p",
    ";p",
    ":p",
    ": p",
    ": - p",
    "(:",
    "( :"
]

HEART = [
    "<3"
]

FROWN = [
    "> : [",
    ":(",
    ": (",
    ": - (",
    ": - [",
    ": [",
    ": @",
    ":'(",
    ": ' (",
    ":/",
    ": /",
    ": \\",
    ":\\",
    "= /",
    "= \\",
    "):",
    ") :"
]

SURPRISE = [
    "> : o",
    ": - o",
    ": O",
    "o_O",
    "8 - 0"
]

ANGRY = [
    ":-||",
    ":@",
    ">:(]"
]

EMOTICONS = {
    "xysmile": SMILE,
    "xyheart": HEART,
    "xyfrown": FROWN,
    "xysurprise": SURPRISE,
    "xyangry": ANGRY
}


def replace_emoticons(text):
    replaceDict = {}
    for replacer in EMOTICONS.keys():
        for replacee in EMOTICONS[replacer]:
            replaceDict[regex.escape(replacee)] = replacer

    prog = regex.compile(LB + "|".join(replaceDict.keys()) + LA)
    return prog.sub(
        lambda match: replaceDict[regex.escape(match.group(0))],
        text
    )


SUBS = {
    "w/": "with",
    "b/": "between",
    "&": "and",
    "'cause": "because",
    "and/or": "and - or",
    "'an": "and",
    "n": "and",
    "'em": "them",
    "attn": "attention",
    "mos": "months",
    "sec": "second",
    "b": "be",
    "r": "are",
    "u": "you",
    "'em": "them",
    "attn": "attention",
    "&amp;": "and",
    "&lt;": "<",
    "&gt;": ">",
    "b4": "before",
    "bc": "because",
    "b/c": "because",
    "btw": "by the way",
    "chk": "check",
    "gr8": "great",
    "ht": "hat tip",
    "idc": "i don't care",
    "idk": "i don't know",
    "imo": "in my opinion",
    "jk": "just kidding",
    "lol": "laugh out loud",
    "nsfw": "not safe for work",
    "ppl": "people",
    "s/o": "shout out",
    "tmb": "tweet me back",
    "ty": "thank you",
    "yw": "you're welcome"
}


def replace_subs(text):
    replaceDict = {}
    for replacee in SUBS.keys():
        replacer = SUBS[replacee]
        replaceDict[regex.escape(replacee)] = replacer

    prog = regex.compile(LB + "|".join(replaceDict.keys()) + LA)
    return prog.sub(
        lambda match: replaceDict[regex.escape(match.group(0))],
        text
    )


def clean(text):
    text = translate_unicodes(text)
    text = replace_links(text)
    text = replace_emoticons(text)
    text = text.lower()
    text = replace_subs(text)

    return text
