{
    'name': 'CRM Sales Visit Tracking',
    'version': '16.0.1.0.0',
    'category': 'CRM',
    'summary': 'Track sales visits, calls, meetings and generated leads with dealer forwarding',
    'depends': ['crm', 'sales_team', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/sales_visit.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}