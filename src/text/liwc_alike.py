#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2014 tiptap. All rights reserved.

Messy attempt to duplicate the text analysis performed
by LIWC

"""
import re
from nltk.tokenize import RegexpTokenizer

PUNCT_MAPPING = {
    '.': "Period",
    ',': "Comma",
    ':': "Colon",
    ';': "SemiC",
    '?': "QMark",
    '!': "Exclam",
    '-': "Dash",
    '\"': "Quote",
    '\'': "Apostro"
}

PAREN_LIST = ['(', ')', '[', ']', '{', '}']

# TOKEN_REGEXP = r"(\w+[^\s]*\w+)|(\w)"
TOKEN_REGEXP = u"([\u0080-\uffff\w]+[^\s]*\w+)|(\w)"
PUNCT_REGEXP = u"([^\u0080-\uffff\x00-\x1f\s\w])"
EXTRA_DASH_REGEXP = r"(\w+-\w+)"
NUMERAL_REGEXP = r"(^\d+[,\.]*\d+[\W]?$)|(^\d+$)"

TRAN_TAB = {
    ord(u'\u2013'): u'-',
    ord(u'\u2018'): u'\'',
    ord(u'\u2019'): u'\'',
    ord(u'\u201c'): u'\"',
    ord(u'\u201d'): u'\"',
}


class LIWCAlike(object):
    def __init__(self, liwctionary):
        self.words = liwctionary.words
        self.wilds = liwctionary.wilds
        self.buckets = liwctionary.buckets

        self.dashTokenizer = RegexpTokenizer("-", gaps=True)

        self.dictCounts = {}
        for bucketNum in self.buckets.keys():
            self.dictCounts[bucketNum] = 0

        self.counts = {}
        self.counts['Sixltr'] = 0
        self.counts['Dic'] = 0
        self.counts['Numerals'] = 0

        for punct in PUNCT_MAPPING.keys():
            self.counts[PUNCT_MAPPING[punct]] = 0

        self.counts['Parenth'] = 0
        self.counts['OtherP'] = 0

    def analyze(self, text):
        text = text.lower()
        text = text.translate(TRAN_TAB)

        self._analyze_punctuation(text)
        tokens = self._analyze_words_and_numerals(text)
        for bucketNum in self.buckets.keys():
            bucketName = self.buckets[bucketNum]
            self.counts[bucketName] = self.dictCounts[bucketNum]

        results = {}
        results['WC'] = self.counts['WC']
        wc = float(self.counts['WC'])

        for name in self.counts:
            if name == 'Parenth':
                results[name] = float(self.counts[name]) / wc * 50
            elif name != 'WC':
                results[name] = float(self.counts[name]) / wc * 100

        return results, tokens

    def _analyze_punctuation(self, text):
        punctTokens = RegexpTokenizer(PUNCT_REGEXP).tokenize(text)
        punctKeys = PUNCT_MAPPING.keys()

        for punct in punctTokens:
            if punct in punctKeys:
                self.counts[PUNCT_MAPPING[punct]] += 1
            elif punct in PAREN_LIST:
                self.counts['Parenth'] += 1
            else:
                self.counts['OtherP'] += 1

        self.counts['AllPct'] = len(punctTokens)

    def _analyze_words_and_numerals(self, text):
        tokens = RegexpTokenizer(TOKEN_REGEXP).tokenize(text)
        self.counts['WC'] = len(tokens)

        for i in range(len(tokens)):
            if re.match(NUMERAL_REGEXP, tokens[i]):
                self.counts['Numerals'] += 1

            bucketList = self._analyze_token(tokens, i)
            tokens[i] = [tokens[i]] + bucketList
            for bucket in bucketList:
                self.dictCounts[bucket] += 1

        return tokens

    def _analyze_token(self, tokens, index):
        if len(tokens[index]) > 6:
            self.counts['Sixltr'] += 1

        prevToken = None
        if index > 0:
            prevToken = tokens[index - 1]

        #  get "nextWord"
        #   - nextWord is None if we are analyzing the last token
        #   - nextWord is None if the next token is hyphenated
        nextWord = None
        dashTokenizer = RegexpTokenizer("-", gaps=True)
        if (index + 1) < len(tokens):
            nextWords = dashTokenizer.tokenize(tokens[index + 1])
            if len(nextWords) == 1:
                nextWord = nextWords[0]

        # now do a second round of tokenization for hyphenated words
        # and concatenate the buckets for each of the hyphenated words.
        #
        # if the first of the hyphenated words is a wildcard, return
        # the bucket for that word only (I have no idea why LIWC works
        # that way)

        words = dashTokenizer.tokenize(tokens[index])
        bucketList = []

        firstIsWild = self.wilds.longest_prefix(words[0], default=None)
        if firstIsWild:
            return self._bucket_list(words[0], prevToken, nextWord)

        self.counts['WC'] += len(words) - 1
        self.counts['Dash'] += len(words) - 1
        for i in range(len(words)):
            bucketList += self._bucket_list(words[i], prevToken, nextWord)

        return bucketList

    def _bucket_list(self, word, prevToken, nextWord):
        rules = self._get_rules(word)
        if rules:
            if "bucketList" in rules.keys():
                return rules['bucketList']

            elif 'likeList' in rules.keys():
                useIndex = 2

                if prevToken:
                    prevBuckets = prevToken[1:]
                    for bucket in rules['likeList'][0]:
                        if bucket in prevBuckets:
                            useIndex = 1
                            break

                return rules['likeList'][useIndex]

            elif 'proxList' in rules.keys():
                bucketList = []
                for proxList in rules['proxList']:
                    if nextWord == proxList[0]:
                        bucketList.append(proxList[1])
                    else:
                        bucketList.append(proxList[2])
                return bucketList

        return []

    def _get_rules(self, word):
        rules = None
        fromWords = self.words.get(word)
        if fromWords:
            self.counts['Dic'] += 1
            rules = fromWords
        else:
            fromWilds = self.wilds.longest_prefix_value(word, default=None)
            if fromWilds:
                self.counts['Dic'] += 1
                rules = fromWilds

        return rules
