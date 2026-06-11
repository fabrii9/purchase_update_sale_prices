# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from markupsafe import Markup


class PurchasePriceUpdateWizard(models.TransientModel):
    _name = 'purchase.price.update.wizard'
    _description = 'Wizard para Actualizar Precios de Venta desde Compra'

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Orden de Compra',
        required=True,
        readonly=True,
        default=lambda self: self.env.context.get('default_purchase_order_id'),
    )
    percentage = fields.Float(
        string='Porcentaje de Recargo (%)',
        required=True,
    )

    @api.constrains('percentage')
    def _check_percentage(self):
        for wiz in self:
            if wiz.percentage <= 0:
                raise UserError(_('El porcentaje de recargo debe ser mayor a cero.'))

    def apply_update(self):
        self.ensure_one()
        order = self.purchase_order_id

        if not order or order.state not in ('purchase', 'done'):
            raise UserError(_('La orden de compra debe estar confirmada o finalizada para actualizar precios.'))

        valid_lines = order.order_line.filtered(
            lambda l: l.product_id
            and l.product_id.type in ('product', 'consu')
            and l.qty_received > 0
            and l.price_unit > 0
        )

        if not valid_lines:
            raise UserError(_('No hay productos recibidos válidos para actualizar precios en esta orden.'))

        # Si un producto aparece varias veces, usar la última línea válida (orden natural por id)
        last_line_by_product = {}
        for line in valid_lines:
            last_line_by_product[line.product_id.id] = line

        update_lines_vals = []
        for line in last_line_by_product.values():
            product = line.product_id
            tmpl = product.product_tmpl_id
            old_price = tmpl.list_price or 0.0
            # Nota: se usa price_unit directamente como base.
            # Si en el futuro se requiere conversión de moneda, modificar aquí.
            purchase_price = line.price_unit
            new_price = purchase_price * (1 + self.percentage / 100.0)

            # Actualizar precio de venta en la plantilla del producto
            tmpl.write({'list_price': new_price})

            update_lines_vals.append({
                'product_id': product.id,
                'product_tmpl_id': tmpl.id,
                'purchase_line_id': line.id,
                'old_sale_price': old_price,
                'purchase_price': purchase_price,
                'percentage': self.percentage,
                'new_sale_price': new_price,
                'qty_received': line.qty_received,
                'currency_id': order.currency_id.id,
            })

        # Crear registro de historial
        history = self.env['purchase.sale.price.update'].create({
            'purchase_order_id': order.id,
            'percentage': self.percentage,
            'product_count': len(update_lines_vals),
            'line_ids': [(0, 0, vals) for vals in update_lines_vals],
        })

        # Mensaje en el chatter de la orden de compra
        msg_body = _(
            'Se actualizaron %(count)s precios de venta con un recargo del %(percentage)s%%. '
            'Historial: <a href="#" data-oe-model="purchase.sale.price.update" data-oe-id="%(history_id)s">%(history_name)s</a>',
            count=history.product_count,
            percentage=self.percentage,
            history_id=history.id,
            history_name=history.name,
        )
        order.message_post(body=Markup(msg_body))

        # Abrir el historial creado
        return {
            'name': _('Actualización de Precios'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.sale.price.update',
            'res_id': history.id,
            'view_mode': 'form',
            'target': 'current',
        }
