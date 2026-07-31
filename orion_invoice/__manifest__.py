{
    'name': 'Orion Invoice Customization',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Adds Orion Details tab in Sales Invoice form',
    'author': 'Sarthak Pradip Samgir',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/orion_details.xml',  # Include your XML view file
        'views/packing_list_menu_tab.xml',
    ],
    'license': 'LGPL-3',
    'application': False,
}
