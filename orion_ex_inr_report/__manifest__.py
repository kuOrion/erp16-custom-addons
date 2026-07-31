{
    'name': 'Orion Export dollar to inr Report',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'Sarthak Pradip Samgir',
    'summary': 'For getting this report before that make changes in account > configuration > currencies > USD '
               'make changes in Rates put current exchange value in (INR PER UNIT)',
    'description': 'Custom Invoice Report with Py3o',
    'depends': ['base', 'account', 'sale', 'report_py3o'],
    'data': [
        'views/inr_report.xml',
        'views/report_button.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',

}