# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PurchaseSalePriceUpdate(models.Model):
    _name = 'purchase.sale.price.update'
    _description = 'Historial de Actualización de Precios de Venta desde Compra'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Número',
        required=True,
        copy=False,
        readonly=True,
        default='Nuevo',
    )
    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Orden de Compra',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Usuario',
        required=True,
        readonly=True,
        default=lambda self: self.env.user,
    )
    date = fields.Datetime(
        string='Fecha',
        required=True,
        readonly=True,
        default=lambda self: fields.Datetime.now(),
    )
    percentage = fields.Float(
        string='Porcentaje de Recargo (%)',
        required=True,
        readonly=True,
    )
    product_count = fields.Integer(
        string='Cantidad de Productos',
        readonly=True,
    )
    line_ids = fields.One2many(
        comodel_name='purchase.sale.price.update.line',
        inverse_name='update_id',
        string='Líneas de Actualización',
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        required=True,
        readonly=True,
        default=lambda self: self.env.company,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Nuevo') == 'Nuevo':
                vals['name'] = self.env['ir.sequence'].next_by_code('purchase.sale.price.update') or 'Nuevo'
        return super(PurchaseSalePriceUpdate, self).create(vals_list)


class PurchaseSalePriceUpdateLine(models.Model):
    _name = 'purchase.sale.price.update.line'
    _description = 'Línea de Historial de Actualización de Precios'

    update_id = fields.Many2one(
        comodel_name='purchase.sale.price.update',
        string='Actualización',
        required=True,
        ondelete='cascade',
    )
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Producto',
        required=True,
        readonly=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Plantilla de Producto',
        required=True,
        readonly=True,
    )
    purchase_line_id = fields.Many2one(
        comodel_name='purchase.order.line',
        string='Línea de Compra',
        readonly=True,
    )
    old_sale_price = fields.Float(
        string='Precio de Venta Anterior',
        readonly=True,
    )
    purchase_price = fields.Float(
        string='Precio de Compra',
        readonly=True,
    )
    percentage = fields.Float(
        string='Porcentaje Aplicado',
        readonly=True,
    )
    new_sale_price = fields.Float(
        string='Nuevo Precio de Venta',
        readonly=True,
    )
    qty_received = fields.Float(
        string='Cantidad Recibida',
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañía',
        related='update_id.company_id',
        store=True,
        readonly=True,
    )
