# Final module for generating manufacturing order report using py3o odt
# imppp
{
    'name': 'Orion manufacturing Done',
    'depends': ['base', 'product', 'mrp'],
    'data': [
        'views/mfg_done.xml',
        'views/py3o_mfg_done.xml',

        'security/ir.model.access.csv',

    ],
    'installable': True,
    'license': 'LGPL-3',

}
