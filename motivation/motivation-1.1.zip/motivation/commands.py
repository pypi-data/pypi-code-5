#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import random
import re

from six.moves import html_parser

import requests
import pmxbot
from pmxbot.core import command
from pmxbot.karma import Karma

@command('pm', aliases=('piratemotivate',), doc='Arggh matey')
def pm(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel

    if random.random() > 0.95:
        return "Arrggh ye be doin' great, grand work, %s!" % rcpt
    return "Arrggh ye be doin' good work, %s!" % rcpt


@command('lm', aliases=('latinmotivate',), doc='Rico Suave')
def lm(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel
    return '¡Estás haciendo un buen trabajo, %s!' % rcpt

@command('fm', aliases=('frenchmotivate',), doc='pmxbot parle français')
def fm(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel
    return 'Vous bossez bien, %s!' % rcpt

@command('jm', aliases=('japanesemotivate',), doc='')
def jm(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel

    hon_romaji = ' san'
    hon_ja = ' さん'

    # Use correct honorific.
    bosses = pmxbot.config.get('bosses', set())
    if any(rcpt.lower().startswith(boss_nick) for boss_nick in bosses):
        hon_romaji = ' sensei'
        hon_ja = ' 先生'

    elif rcpt == channel:
        hon_romaji = ''
        hon_ja = ''

    emoji = '(^_−)−☆'

    # reference the vars to avoid linter warnings
    emoji, hon_romaji, hon_ja

    return (
        '{rcpt}{hon_ja}, あなたわよくやっています! '
        '({rcpt}{hon_romaji}, anata wa yoku yatte '
        'imasu!)  -  {emoji}'.format(**vars())
    )

@command('danke', aliases=('dankeschoen','ds'), doc='Danke schön!')
def danke(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 1)
        rcpt = rest
    else:
        rcpt = channel
    return 'Danke schön, {rcpt}! Danke schön!'.format(rcpt=rcpt)


@command('gm', aliases=('germanmotivate',), doc='German motivate')
def gm(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 1)
        rcpt = rest
    else:
        rcpt = channel
    return "Du leistest gute Arbeit, %s!" % rcpt


@command('esperantomotivate', aliases=('em',), doc='Esperanto motivate')
def em(client, event, channel, nick, rest):
    if rest:
        rest = rest.strip()
        Karma.store.change(rest, 2)
        rcpt = rest
    else:
        rcpt = channel
    return 'Vi faras bonan laboron, {rcpt}!'.format(rcpt=rcpt)

@command('schneier', doc='schneier "facts"')
def schneier(client, event, channel, nick, rest):
    rcpt = rest.strip() or channel
    if rest.strip():
        Karma.store.change(rcpt, 2)

    url = 'http://www.schneierfacts.com/'
    d = requests.get(url).text
    start_tag = re.escape('<p class="fact">')
    end_tag = re.escape('</p>')
    p = re.compile(start_tag + '(.*?)' + end_tag,
        flags=re.DOTALL | re.MULTILINE)
    match = p.search(d)

    if not match:
        return "Sorry, no facts found (check your crypto anyway)."
    phrase = match.group(1).replace('\n', ' ').strip()
    if rcpt != channel:
        phrase = phrase.replace('Bruce Schneier', rcpt)

    # unescape HTML
    h = html_parser.HTMLParser()
    phrase = h.unescape(phrase)

    return phrase
