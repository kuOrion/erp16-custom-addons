{
    'name': 'Orion specifications',
    'version': '1.0',
    'license': 'LGPL-3',

    'depends': ['base', 'product', 'sale_product_configurator', 'sale', 'sale_management'],
    # Ensure 'sale' and 'report_py3o' are listed
    'data': [
        'views/specification_tab.xml', ],
    'author': 'sarthak samgir',
    'installable': True,
    'application': True,
    'auto_install': False,  # Changed to False unless auto-install is required
    'sequence': 200,
    'license': 'LGPL-3'
}
