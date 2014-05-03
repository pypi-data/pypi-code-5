#!/usr/bin/python
#-*- coding: utf-8 -*-

# Copyright (c) 2013 Eric F <efigue> Figerson
# Author(s):
#   Eric F <eric.foss@free.fr>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import csv
import os
import sys
import decimal
import facct.config as config
from facct.i18n import _

# TODO: These lines should be factorized:
DEBIT, CREDIT = range(2)
zero = decimal.Decimal(0)
epsilon = 0
def get_float(str):
    if type(str) == type(zero):
        return str
    if not str:
         return zero
    else:
         return decimal.Decimal(str.replace(',', '.'))

class IncomeStatement:
    def __init__(self, balance=None, orga=None, year=None):
        self._bal = balance
        if balance:
            self._year = balance._year
            self._orga = balance._orga
        else:
            self._year = year
            self._orga = orga

    def load_and_save_year(self):
        def deb(a):
            if not self._bal.read_bal_account(a)[CREDIT] and\
                not self._bal.read_bal_account(a)[DEBIT]:
                return 0
            if self._bal.read_bal_account(a)[DEBIT]:
                return self._bal.read_bal_account(a)[DEBIT]
            else:
                return - self._bal.read_bal_account(a)[CREDIT]

        def cred(a):
            return self._bal.read_bal_account(a)[CREDIT]

        def getProfit(value):
            if value>0:
                return abs(value)
            else:
                return 0
        def getLoss(value):
            if value<0:
                return abs(value)
            else:
                return 0
        external_expenses = [
                616400, 618000, 618300, 622700, 625000, 626000, 627000]
        charges = [("Charges d'exploitation :\nAchat de marchandises", 0),
        ("Variation de stocks (marchandises)", 0),
        ("Achats d'approvisionnements", deb(606400)),
        ("Variations de stocks (approvisionnements)", 0),
        ("Autres charges externes", sum([deb(x) for x in external_expenses])),
        ("Impôts, taxes et versements assimilés", deb(635110)),
        ("Rémunérations du personnel", deb(644000)),
        ("Charges sociales", sum([deb(x) for x in [645100, 645300, 645800]])),
        ("Dotations aux amortissements", 0),
        ("Dotations aux provisions", 0),
        ("Autres charges", 0),
        ("Charges financières", deb(627800)),
        ["Total I", 0],
        ("Charges exceptionnelles (II)", deb(671200)),
        ("Impôts sur les bénéfices (III)", deb(695000)),
        ["Total des charges (I +II+ III)", 0],
        ("Solde créditeur : bénéfice (I)", getProfit(self._bal.net_profit)),
        ["TOTAL GENERAL", 0]]
        charges[12][1] = sum(c[1] for c in charges[:12])
        charges[15][1] = sum(c[1] for c in charges[12:15])
        charges[17][1] = sum(c[1] for c in charges[15:17])

        income = [("Produits d'exploitation :\nVentes de marchandises", 0),
        ("Production vendue (biens et services)", cred(706000)),
        ("Production stockée", 0),
        ("Production immobilisée", 0),
        ("Subventions d'exploitation", 0),
        ("Autres produits", 0),
        ("Produits financiers", 0),
        ["Total I", 0],
        ("dont à l’exploitation :", 0),
        ("Produits exceptionnels (II)", 0),
        ["Total des produits (I+II)", 0],
        ("Solde débiteur : perte", getLoss(self._bal.net_profit)),
        ["TOTAL GENERAL", 0],
        ('', 0),
        ('', 0),
        ('', 0),
        ('', 0),
        ('', 0), ]
        income[7][1] = sum(c[1] for c in income[:7])
        income[10][1] = sum(c[1] for c in income[7:10])
        income[12][1] = sum(c[1] for c in income[10:12])

        self._charges = charges
        self._produits = income
        if len(charges) != len(income):
            sys.stderr.write(_(
                        'charges and income number lines are different!\n'))
            sys.exit(2)
        txt_info = _('Income statement: charges and income totals are')
        if abs(charges[-1][1] - income[12][1]) > decimal.Decimal(epsilon):
            sys.stderr.write(_('{0} different! charges={1}, income={2}\n'
                        ).format(txt_info, charges[-1][1], income[12][1]))
            sys.exit(2)
        else:
            sys.stdout.write(_('%s are equal!\n') % txt_info)

    def get_file_name(self, year=None):
        if not year:
            year = self._year
        return os.path.join(config.get_accounts_dir(self._orga),
                '%s' % year, 'IncomeStatement_%s.csv' % year)

    def load_previous_year(self):
        file_income_statement = self.get_file_name(self._year - 1)
        self.prev_income_stat = []
        if os.path.exists(file_income_statement):
            reader = csv.reader(open(file_income_statement, 'r'),
                    delimiter=',', quotechar='"')
            for row in reader:
                self.prev_income_stat.append(dict(zip([ 'charges_name',
                    'charges_val', 'prev_charges', 'products_name',
                    'products_val', 'prev_produits'], row)))

    def get_prev_year(self, line, column):
        if not self.prev_income_stat or line >= len(self.prev_income_stat):
            return ''
        return self.prev_income_stat[line][column]

    def getValue(self, valueName):
        if not self.prev_income_stat:
            return 0
        for row_dict in self.prev_income_stat:
            if row_dict['products_name'] == valueName:
                return get_float(row_dict['products_val'].strip())
        return 0

    def write_csv(self):
        writer = csv.writer(open(self.get_file_name(), 'w'),
                delimiter=',', quotechar='"')
        for i in range(len(self._charges)):
            writer.writerow([self._charges[i][0],
                '%.2f' % round(self._charges[i][1],2),
                self.get_prev_year(i, 'charges_val'),
                self._produits[i][0],
                '%.2f' % round(self._produits[i][1],2),
                self.get_prev_year(i, 'products_val')])

    def getPreviousLosses(self):
        self.load_previous_year()
        return self.getValue('Solde débiteur : perte')

    def corpTaxCalculation(self, gross_profit):
        tax = 0
        SS_ceiling = 38120
        fiscalProfit = gross_profit - self.getPreviousLosses()
        if fiscalProfit>=0:
            tax = fiscalProfit*15/100
        if fiscalProfit>=SS_ceiling:
            tax += (fiscalProfit-SS_ceiling)/3
        return decimal.Decimal(tax).quantize(
                decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_DOWN)

