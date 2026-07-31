# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

{
    'name' : 'Product Configurator',
    'version' : '16.0.12',
    'summary': 'Product Configurator',
    'sequence': 10,
    'post_init_hook': 'post_init_hook',
    'description': """ Product Configurator """,
    'category': 'Accounting/Accounting',
    'depends' : ['sale', 'sale_management', 'sale_product_configurator', 'mrp'],
    'data': [

        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "views/product_template_views.xml",
        "views/product_views.xml",
        "views/prodcut_attributes_views.xml",
        "views/product_template_attribute_value_views.xml",
        "views/res_config_setting_ref_view.xml",
        "views/templates.xml",
        "views/variant_templates.xml",

    ],
    'assets': {
        'web.assets_backend': [
            'sh_product_configurator/static/src/js/sale_product_field.js',
            'sh_product_configurator/static/src/js/product_configurator_modal.js',
            'sh_product_configurator/static/src/js/variant_mixin.js',
            'sh_product_configurator/static/src/js/list_renderer_patch.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
