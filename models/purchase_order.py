# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    show_update_sale_prices_button = fields.Boolean(
        string='Mostrar botón actualizar precios',
        compute='_compute_show_update_sale_prices_button',
    )

    @api.depends('state', 'order_line.qty_received')
    def _compute_show_update_sale_prices_button(self):
        for order in self:
            if order.state not in ('purchase', 'done'):
                order.show_update_sale_prices_button = False
                continue
            has_received = any(line.qty_received > 0 for line in order.order_line)
            order.show_update_sale_prices_button = has_received

    def action_open_sale_price_update_wizard(self):
        self.ensure_one()
        return {
            'name': 'Actualizar Precios de Venta',
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.price.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_purchase_order_id': self.id,
            },
        }
