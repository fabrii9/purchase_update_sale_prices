# -*- coding: utf-8 -*-
{
    'name': 'Actualizar Precios de Venta desde Compra',
    'version': '18.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Actualiza precios de venta desde la orden de compra recibida aplicando un recargo sobre el costo.',
    'description': """
        Desde una orden de compra confirmada con mercadería recibida, permite abrir un wizard
        para aplicar un porcentaje de recargo sobre el precio de compra y actualizar el
        precio de venta (list_price) de los productos. Genera un historial completo por operación.
    """,
    'author': 'Senior Odoo Dev',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'purchase',
        'stock',
        'product',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/purchase_price_update_wizard_views.xml',
        'views/price_update_views.xml',
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
