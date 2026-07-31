{
    'name': 'Orion sale',
    'version': '1.0',
    'license': 'LGPL-3',

    'depends': ['base', 'product', 'sale_product_configurator', 'sale', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',

        # 'views/specification_tab.xml',
        # 'views/internal_ref.xml',
        'views/quotation_fields.xml',
        'views/product.xml',
        'views/total_value_sales_quotation_list.xml',
        # 'views/form_orderline.xml',
    ],
    'author': 'sarthak samgir',
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 200,
    'license': 'LGPL-3'
}
