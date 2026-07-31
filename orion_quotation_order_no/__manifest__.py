{
    'name': 'Orion Custom Sale Sequence for quotation and order',
    'version': '16.0.1.0.0',
    'depends': ['sale'],
    'category': 'Sales',
    'summary': 'Custom Quotation and Sale Order Sequences',
    'data': [
        # 'data/sale_order_sequence.xml',
        'security/ir.model.access.csv',

        'views/res_config_settings_views.xml',
        'views/quotaions_orderes_seperation.xml',
        'views/confirm_button_validation.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
}
