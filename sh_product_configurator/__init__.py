# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from . import models
from . import controllers
from odoo import  api, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    products = env['product.product'].search([])
    products.write({'sh_is_record_saved': True})
    cr.commit()  # Commit changes to the database
