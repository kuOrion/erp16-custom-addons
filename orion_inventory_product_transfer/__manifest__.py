{
    'name': 'orion inventory product transfer',
    'category': 'production',
    'description': """created product transfer between different locations pdi to fg and fg to stock """,
    'author': 'Sarthak Pradip Samgir',
    'depends': ['stock','mrp'],
    'data': [
        'views/mrp_config_setting.xml',
        'views/mrp.xml',
        'views/action_pdi_to_fg.xml',
        'security/ir.model.access.csv',

    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',

}
