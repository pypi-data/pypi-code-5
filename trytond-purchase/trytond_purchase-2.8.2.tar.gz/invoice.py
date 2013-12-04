#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, Workflow, fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.backend import TableHandler

__all__ = ['Invoice', 'InvoiceLine']
__metaclass__ = PoolMeta


class Invoice:
    __name__ = 'account.invoice'
    purchase_exception_state = fields.Function(fields.Selection([
        ('', ''),
        ('ignored', 'Ignored'),
        ('recreated', 'Recreated'),
        ], 'Exception State'), 'get_purchase_exception_state')
    purchases = fields.Many2Many('purchase.purchase-account.invoice',
            'invoice', 'purchase', 'Purchases', readonly=True)

    @classmethod
    def __setup__(cls):
        super(Invoice, cls).__setup__()
        cls._error_messages.update({
                'delete_purchase_invoice': ('You can not delete invoices '
                    'that come from a purchase.'),
                'reset_invoice_purchase': ('You cannot reset to draft '
                    'an invoice generated by a purchase.'),
                })

    @classmethod
    def get_purchase_exception_state(cls, invoices, name):
        Purchase = Pool().get('purchase.purchase')
        with Transaction().set_user(0, set_context=True):
            purchases = Purchase.search([
                    ('invoices', 'in', [i.id for i in invoices]),
                    ])

        recreated = tuple(i for p in purchases for i in p.invoices_recreated)
        ignored = tuple(i for p in purchases for i in p.invoices_ignored)

        res = {}
        for invoice in invoices:
            if invoice in recreated:
                res[invoice.id] = 'recreated'
            elif invoice in ignored:
                res[invoice.id] = 'ignored'
            else:
                res[invoice.id] = ''
        return res

    @classmethod
    def delete(cls, invoices):
        cursor = Transaction().cursor
        if invoices:
            cursor.execute('SELECT id FROM purchase_invoices_rel '
                'WHERE invoice IN (' + ','.join(('%s',) * len(invoices)) + ')',
                [i.id for i in invoices])
            if cursor.fetchone():
                cls.raise_user_error('delete_purchase_invoice')
        super(Invoice, cls).delete(invoices)

    @classmethod
    def copy(cls, invoices, default=None):
        if default is None:
            default = {}
        default = default.copy()
        default.setdefault('purchases', None)
        return super(Invoice, cls).copy(invoices, default=default)

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, invoices):
        Purchase = Pool().get('purchase.purchase')
        with Transaction().set_user(0, set_context=True):
            purchases = Purchase.search([
                    ('invoices', 'in', [i.id for i in invoices]),
                    ])
        if purchases and any(i.state == 'cancel' for i in invoices):
            cls.raise_user_error('reset_invoice_purchase')

        return super(Invoice, cls).draft(invoices)

    @classmethod
    def paid(cls, invoices):
        pool = Pool()
        Purchase = pool.get('purchase.purchase')
        super(Invoice, cls).paid(invoices)
        with Transaction().set_user(0, set_context=True):
            Purchase.process([p for i in cls.browse(invoices)
                    for p in i.purchases])

    @classmethod
    def cancel(cls, invoices):
        pool = Pool()
        Purchase = pool.get('purchase.purchase')
        super(Invoice, cls).cancel(invoices)
        with Transaction().set_user(0, set_context=True):
            Purchase.process([p for i in cls.browse(invoices)
                    for p in i.purchases])


class InvoiceLine:
    __name__ = 'account.invoice.line'

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().cursor

        super(InvoiceLine, cls).__register__(module_name)

        # Migration from 2.6: remove purchase_lines
        rel_table = 'purchase_line_invoice_lines_rel'
        if TableHandler.table_exist(cursor, rel_table):
            cursor.execute('SELECT purchase_line, invoice_line '
                'FROM "' + rel_table + '"')
            for purchase_line, invoice_line in cursor.fetchall():
                cursor.execute('UPDATE "' + cls._table + '" '
                    'SET origin = %s '
                    'WHERE id = %s',
                    ('purchase.line,%s' % purchase_line, invoice_line))
            TableHandler.drop_table(cursor,
                'purchase.line-account.invoice.line', rel_table)

    @classmethod
    def _get_origin(cls):
        models = super(InvoiceLine, cls)._get_origin()
        models.append('purchase.line')
        return models
