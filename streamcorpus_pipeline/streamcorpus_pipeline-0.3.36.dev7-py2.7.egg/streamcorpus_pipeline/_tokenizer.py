#!/usr/bin/env python
'''
streamcorpus_pipeline.TaggerBatchTransform for LingPipe

This software is released under an MIT/X11 open source license.

Copyright 2012-2013 Diffeo, Inc.
'''
import os
import re
import sys
import uuid
import time
import hashlib
import logging
import itertools
import traceback
import streamcorpus
from sortedcollection import SortedCollection
from streamcorpus_pipeline.stages import IncrementalTransform
from nltk.tokenize import WhitespaceTokenizer
from nltk.tokenize.punkt import PunktWordTokenizer, PunktSentenceTokenizer
from streamcorpus import Token, Sentence, EntityType, Chunk, Offset, OffsetType, Gender, MentionType, Attribute, AttributeType

from _taggers import TaggerBatchTransform

logger = logging.getLogger('streamcorpus_pipeline.nltk_tokenizer')

class nltk_tokenizer(IncrementalTransform):
    '''
    a streamcorpus_pipeline IncrementalTransform that converts a chunk into a new
    chunk with Sentence objects generated using NLTK tokenizers
    '''
    tagger_id = 'nltk_tokenizer'
    def __init__(self, config):
        self.config = config
        self.sentence_tokenizer = PunktSentenceTokenizer()
        self.word_tokenizer = WhitespaceTokenizer() #PunktWordTokenizer()

    def _sentences(self, clean_visible):
        'generate strings identified as sentences'
        for start, end in self.sentence_tokenizer.span_tokenize(clean_visible):
            ## no need to check start, because the first byte of text
            ## is always first byte of first sentence, and we will
            ## have already made the previous sentence longer on the
            ## end if there was an overlap.
            try:
                label = self.label_index.find_le(end)
            except ValueError:
                label = None
            if label:
                off = label.offsets[OffsetType.BYTES]
                end = max(off.first + off.length, end)
            yield start, end, clean_visible[start:end]

    def make_label_index(self, stream_item):
        labels = stream_item.body.labels.get(self.config.get('annotator_id'))
        if not labels:
            labels = []

        self.label_index = SortedCollection(
            labels,
            key=lambda label: label.offsets[OffsetType.BYTES].first)

    def make_sentences(self, stream_item):
        self.make_label_index(stream_item)
        sentences = []
        token_num = 0
        new_mention_id = 0
        for sent_start, sent_end, sent_str in self._sentences(stream_item.body.clean_visible):
            sent = Sentence()
            sentence_pos = 0
            for start, end in self.word_tokenizer.span_tokenize(sent_str):
                tok = Token(
                    token_num=token_num,
                    token=sent_str[start:end],
                    sentence_pos=sentence_pos,
                )
                ## whitespace tokenizer will never get a token
                ## boundary in the middle of an 'author' label
                try:
                    label = self.label_index.find_le(sent_start + start)
                except ValueError:
                    label = None
                if label:
                    off = label.offsets[OffsetType.BYTES]
                    if off.first + off.length > sent_start + start:
                        ## overlaps
                        streamcorpus.add_annotation(tok, label)
                        logger.info('adding label to tok: %r has %r',
                                     tok.token, label.target.target_id)

                        if label in self.label_to_mention_id:
                            mention_id = self.label_to_mention_id[label]
                        else:
                            mention_id = new_mention_id
                            new_mention_id += 1
                            self.label_to_mention_id[label] = mention_id

                        tok.mention_id = mention_id
                token_num += 1
                sentence_pos += 1
                sent.tokens.append(tok)
            sentences.append(sent)
        return sentences

    def process_item(self, stream_item, context=None):
        if not hasattr(stream_item.body, 'clean_visible') or not stream_item.body.clean_visible:
            return stream_item
            
        self.label_index = None
        self.label_to_mention_id = dict()
        stream_item.body.sentences[self.tagger_id] = self.make_sentences(stream_item)

        return stream_item

    def __call__(self, stream_item, context=None):
        ## support the legacy callable API
        self.process_item(stream_item, context)
        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    args = parser.parse_args()

    logger = logging.getLogger('streamcorpus_pipeline')
    ch = logging.StreamHandler()
    logger.addHandler(ch)
    streamcorpus_logger = logging.getLogger('streamcorpus')
    streamcorpus_logger.addHandler(ch)

    t = nltk_tokenizer(dict(annotator_id='author'))
    for si in Chunk(args.input):
        t.process_item(si)
        if si.body.clean_visible:
            assert len(si.body.sentences['nltk_tokenizer']) > 0
            logger.critical( 'num_sentences=%d, has wikipedia %r and %d labels',
                             len(si.body.sentences['nltk_tokenizer']),  
                             'wikipedia.org' in si.body.clean_html,
                             len(getattr(si.body, 'labels', {}).get('author', {})) )

            #if len(getattr(si.body, 'labels', {}).get('author', {})) > 3:
            #    c = Chunk('foo.sc', mode='wb')
            #    c.add(si)
            #    c.close()
            #    sys.exit()
        
