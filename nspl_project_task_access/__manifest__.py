# -*- coding: utf-8 -*-
{
    "name": "Users Restriction for Project and Task",
    "version": "16.0.1.0.0",
    "category": "Project",
    "summary": "Restrict user access to specific projects and tasks in Odoo",
    "description": """
This module allows you to restrict and control user access to specific projects and tasks.

✔ Grant access to only authorized users  
✔ Prevent unauthorized viewing or editing of tasks and projects  
✔ Improve data security within the project module  
✔ Ideal for managing sensitive or client-specific projects  
""",
    "author": "Namah Softech Private Limited",
    "company": "Namah Softech Private Limited",
    "website": "https://www.namahsoftech.com",
    "support": "support@namahsoftech.com",
    "contributors": ["Vipul Sah"],
    'price': 15.00,
    'currency': 'USD',
    "license": "LGPL-3",
    "depends": ["project"],
    "data": [
        "security/project_task_security.xml",
        "views/project_project_views.xml",
        "views/project_task_views.xml",
    ],
    "images": ["static/description/img/banner.png"],
    "installable": True,
    "auto_install": False,
    "application": False,
}
