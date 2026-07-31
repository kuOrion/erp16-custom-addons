# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

{
    'name' : "Access Management System",
    
    "author": "Softhealer Technologies",

    "license": "OPL-1",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "16.0.2",

    "category": "Extra Tools",

    "summary": "Access Management System Customized Menu Access Field access control Navbar button management Chatter Access Management Report action Management Multiaction views access Role-based access control Customizable user permissions User Role Management Access Control Security Policies Multi-Factor Authentication User Provisioning Access Monitoring Access Management System module User Access Control software Access Management solution Access Control System tool Manage Access Management of user access manage access All in one access control all in one access management User wise access rules user wise access control user wise access management hide menu hide any menu hide sub menu disable menu disable submenu disable any menu invisible menu hide menus usewise hide menu user wise menu hide submenus hide menus Hide field hide fields hide any field disable fields user wise fields invisible field Read only fields hide archive disable action disable delete Hide buttons hide any buttons disable button user wise buttons invisible button Hide delete hide import hide export hide actions Hide tabs hide any tabs invisible tab Hide views hide any view hide tree view hide list view hide kanban view hide graph view hide activity view hide apps invisible views hide reports disable reports user wise reports Hide chatter disable chatter invisible chatter Access rights user access roles user security access user wise accesses access rights setup Advanced Users Access Rights Manager Access Rights Management for System User Message Access Rights Model Level Access Rights Field Level Access Rights User Wise Access Rights Setup Access Rules Setup Access Rights Advanced User Access Advance User Access Rights Hide Pivot Hide Object Buttons Hide Action Button Hide Smart Buttons Hide Export Button Hide Import Button Readonly Any Field Hide Create Hide Duplicate Restrict Menu Restrict Any Menu Disable Menu Disable Any Menu Restrict Fields Restrict Any Fields Disable Fields Disable Any Fields Restrict Buttons Restrict Any Buttons Restrict Chatter Hide Send Message Hide Lognote Hide Followers Hide Activities Hide Attachments Restrict Send Message Restrict Lognote Restrict Followers Restrict Activities Restrict Attachments Hide Contacts Restrict Contacts Odoo Access Management App Read Only Users Readonly Users Read only Users Read Only User Read Only Whole System Readonly whole system disable login hide login hide user login Restrict user login Restrict login Disable Buttons Restrict Buttons Hide action buttons Disable action buttons Restrict action buttons Hide Print Buttons Disable Print Buttons Restrict Print Buttons Hide Contacts Disable Menus Restrict Menus Hide Menus Disable submenus Restrict Sub Menus Restrict reports Disable actions Restrict Actions Disable import Restrict Import Restrict Delete Disable Export Restrict Export Disable Archive Restrict Archive Disable Tree view Restrict Tree view Hide Form view Disable Form view Restrict Form view Disable Kanban view Restrict Kanban view Hide Calendar view Disable Calendar view Restrict Calendar view Hide Pivot View Disable Pivot View Restrict Pivot View Disable Graph view Restrict Graph view Disable Apps Restrict Apps Restrict group by Restrict filters advance user access Expenses access rights Quality access rights Quality control access Contacts access rights Rental access rights Calendar access Field Service access rights Restrict Delete items Hide Delete items Disable Delete Items Restrict Fields Restrict Views Disable Views Hide Views Restrict Reports Disable Reports Hide Reports model access rights Time Off access rights Simplify Access Management Recruitment access Rights Employees access rights Knowledge access rights Maintenance access rights Calendar access Field Service access Appointments access Surveys access Multi Company supported User Activity Log Record Log sales user permissions timesheet access rights Timesheets access purchase access rights accounting user permission all in one access rights manager all in one user access all in one user access rights all in one user wise access advance access right manager access rights manager Expenses access Documents access rights Social Marketing access rights  Appraisals access rights Fleet access rights Payroll access rights Surveys access rights Repairs access right Referral access right Attendances access rights Management access rights Shipping access rights Access group management Access organizational structure Access rules setup Easy access rights setup User wise access rules Helpdesk access rights  Subscriptions access rights Readonly system Easier then Record rules setup Show only what is needed for usersHide Calendar view Hide Pivot Hide action buttons Readonly Any Field Readonly Any button read only user Hide create Disable create Restrict Create Hide duplicate Disable duplicate Restrict duplicate Readonly Fields Readonly Any  Fields Invisible Field Chatter Hide Control every fields Control Any fields Control every views Control Any views Control buttons Control Any buttons Control every actions Hide sub-menus Record rules setup Show only what is needed for users Easy access rights setup Access group management Access organizational structure Readonly system Hide sub-menus Hide Calendar view Hide Pivot Hide action buttons Readonly Any Field read only user Hide create Hide duplicate Readonly Field Chatter Hide Control every fields Control every views Control buttons Control every actions Restrict/Read-Only Fields Restrict/Read-Only Export Restrict/Read-Only Archive Restrict/Read-Only Actions Restrict/Read-Only Views Restrict/Read-Only Reports Restrict Delete items Restrict Fields Restrict Export Restrict Archive Restrict Action Restrict Views Restrict Reports Restrict Delete items model access rights sales user permissions inventery access rights timesheet access rights accounting user permission all in one access rights manager Timesheets access Expenses access Documents access Time Off access Recruitment access Employees access Maintenance access Calendar access Field Service access Appointments access Surveys access Multi Company supported User Activity Log Record Log Odoo",
    
    "description": """Do you want to simplify your work environment in an organization with access rights? Then this module improves your work efficiency with Instant Access, a powerful tool that simplifies tasks. Customize who can access essential parts of your work, like Menu, Field, Navbar Button, Chatter, Report Action, and Multiaction Views. With a focus on honesty, Instant Access ensures everyone has the right permissions for their work. This access management system simplifies work processes and helps everyone collaborate better.""",

    'depends' : ['base_setup','web','base','sale_management','mail'],

    'data' : [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/access_manager.xml',
    ],

    'assets': {    
        'web.assets_backend': [
            'sh_access_management/static/src/js/hide_multiactions.js',
            'sh_access_management/static/src/js/chatter_container.js',
            'sh_access_management/static/src/xml/sh_create_access.xml',
            'sh_access_management/static/src/xml/chatter_container.xml',
        ],   
    },
    'demo' : [],
    'installation': True,
    'application' : True,
    'auto_install' : False,
    "images": ["static/description/background.png", ],
    "price": "87.20",
    "currency": "EUR"

}
