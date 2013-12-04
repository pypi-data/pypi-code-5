# -*- coding: utf-8 -*-
#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
{
    'name' : 'Party',
    'name_bg_BG': 'Партньор',
    'name_de_DE': 'Parteien',
    'name_es_CO': 'Terceros',
    'name_es_ES': 'Terceros',
    'name_fr_FR': 'Tiers',
    'name_nl_NL': 'Relaties',
    'name_ru_RU': 'Контрагенты',
    'version': '2.2.3',
    'author' : 'B2CK',
    'email': 'info@b2ck.com',
    'website': 'http://www.tryton.org/',
    'description': 'Define parties, addresses and co.',
    'description_bg_BG': 'Задаване на партньори, адреси и тн.',
    'description_de_DE': 'Ermöglicht die Erstellung von Parteien, Adressen, etc.',
    'description_es_CO': 'Definición de terceros, direcciones, etc.',
    'description_es_ES': 'Define terceros, direcciones, etc...',
    'description_fr_FR': 'Définit des tiers, des adresses, etc.',
    'description_nl_NL': 'Definieert relaties, adressen en bedrijven.',
    'description_ru_RU': 'Определение контрагентов, адресов и тп.',
    'depends' : [
        'ir',
        'res',
        'country',
    ],
    'xml' : [
        'party.xml',
        'category.xml',
        'address.xml',
        'contact_mechanism.xml',
        'configuration.xml',
    ],
    'translation': [
        'locale/bg_BG.po',
        'locale/cs_CZ.po',
        'locale/de_DE.po',
        'locale/es_CO.po',
        'locale/es_ES.po',
        'locale/fr_FR.po',
        'locale/nl_NL.po',
        'locale/ru_RU.po',
    ],
}
