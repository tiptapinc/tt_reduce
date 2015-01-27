#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2014 tiptap. All rights reserved.

Read in and process the LIWC dictionary

"""
import pytrie
import re

PROX_REGEXP = r"(<[\w]+>)([0-9]*)/([0-9]*)"


class LIWCTionary(object):
    def __init__(self):
        self.buckets = {}
        self.words = {}
        self.wilds = pytrie.StringTrie()

        self._load_dict("dictionaries/LIWC2007_English100131.dic")
        self._load_dict("dictionaries/tiptap.dic")

    def _load_dict(self, filename):
        with open(filename) as f:
            lines = f.readlines()

        linerator = iter(lines)
        while True:
            line = linerator.next()
            if line.strip() == "%":
                break

        while True:
            line = linerator.next()
            if line.strip() == "%":
                break

            bucketNum = line.split()[0]
            bucketName = line.split()[1]
            self.buckets[bucketNum] = bucketName

        while True:
            try:
                line = linerator.next()
            except StopIteration:
                break

            word = line.split()[0]
            stringList = line.split()[1:]
            try:
                # most basic rule simply specifies all the buckets
                # to increment when this word is encountered
                intBuckets = [int(bucketStr) for bucketStr in stringList]
                rules = dict(bucketList=[str(bucket) for bucket in intBuckets])
            except ValueError:
                # special-case the non-basic rules
                if word == 'like':
                    # the word 'like' gets special-cased like you read about
                    rules = dict(likeList=[
                        ["2", "134"],
                        ["125", "126", "253"],
                        ["464", "253"]
                    ])
                else:
                    # the only other rule we know how to deal with is
                    # a proximity dependent rule
                    proxList = []
                    for s in stringList:
                        match = re.match(PROX_REGEXP, s)
                        if match:
                            proxList.append(
                                [
                                    match.group(1),
                                    match.group(2),
                                    match.group(3)
                                ]
                            )
                    rules = dict(proxList=proxList)

            if word[-1] == '*':
                self.wilds[word[:-1]] = rules
            else:
                self.words[word] = rules
