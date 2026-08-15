{
    'name': 'Orion Manufacturing Customisation',
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'Manufacturing',
    'sequence': 10,
    'summary': 'Extend Bill of Material with additional fields',

    'author': 'Sarthak Pradip Samgir',
    'depends': ['base','mrp','sale','orion_sales_schedule'],
    'data': [
        'views/mrp_production.xml',
        'views/BOM_internal_ref.xml',
        'views/mrp_production_component_avail.xml',
        # 'wizard/Product_Selection.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'sequence': -100,

}