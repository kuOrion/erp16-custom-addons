{
    'name': 'Invoice Prefix Generator for orion',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Custom invoice numbering with configurable prefix',
    'description': """
        This module allows you to set custom prefixes for invoice numbers
        and automatically generates invoice numbers with the configured prefix.
    """,
    'author': 'orion instruments',
    'depends': ['account', 'base_setup'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'auto_install': True,
    'license': 'LGPL-3',

}
