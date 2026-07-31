from odoo import fields, models, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    calibration = fields.Text('Calibration')

    capillary = fields.Text('Capillary')
    bulb_connection = fields.Text('Bulb Connection')
    differential_temp = fields.Text('Differential Temp ')
    # max_pressure_temp = fields.Text('Max Pressure/Temp')
    repeatability = fields.Text('Repeatability')
    other_wetted_parts = fields.Text('Other Wetted Parts')
    enclosure = fields.Text('Enclosure')
    protective_cap = fields.Text('Protective Cap')
    wetted_parts = fields.Text('Wetted Parts')
    bulletin_no = fields.Text('Bulletin No')
    model_enhancements = fields.Text('Model Enhancements')
    model_category = fields.Text('Model Category')
    on_off_diff = fields.Text('On Off Diff')
    max_pressure_temp = fields.Text('Max Pressure/Temp')
    photo_jpg = fields.Text('Photo JPG')

    # Computed fields
    model_name = fields.Text('Model Name', store=True)
    diaphragm = fields.Text('Diaphragm', store=True)
    micro_switch = fields.Text('Micro Switch',store=True)
    switch_type = fields.Text('Switch Type',store=True)
    range_code = fields.Text('Range Code', store=True)
    range_scale = fields.Text('Range Scale', store=True)
    pressure_port = fields.Text('Pressure Port', store=True)
    pressure_housing = fields.Text('Pressure Housing', store=True)
    cable_entry = fields.Text('Cable Entry', store=True)
    short_name = fields.Text('Short Name', store=True)
    base_type = fields.Text('Base Type', store=True)

    @api.depends('product_template_attribute_value_ids.attribute_value_id')
    def _compute_specifications(self):
        for product in self:
            attr_values = product.product_template_attribute_value_ids.mapped('attribute_value_id')

            # Mapping logic: Extracting specification text based on attribute names
            product.specification = '\n'.join(filter(None, attr_values.mapped('specification')))
            product.model_name = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Model Name' in a.name).mapped('specification')))
            product.range_code = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Range Code' in a.name).mapped('specification')))
            product.on_off_diff = '\n'.join(filter(None, attr_values.filtered(lambda a: 'On Off Diff' in a.name).mapped('specification')))
            product.differential_temp = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Differential Temp' in a.name).mapped('specification')))
            product.repeatability = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Repeatability' in a.name).mapped('specification')))
            product.pressure_housing = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Pressure Housing' in a.name).mapped('specification')))
            product.model_enhancements = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Model Enhancements' in a.name).mapped('specification')))
            product.wetted_parts = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Wetted Parts' in a.name).mapped('specification')))
            product.other_wetted_parts = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Other Wetted Parts' in a.name).mapped('specification')))
            product.protective_cap = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Protective Cap' in a.name).mapped('specification')))
            product.calibration = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Calibration' in a.name).mapped('specification')))
            product.capillary = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Capillary' in a.name).mapped('specification')))
            product.bulb_connection = '\n'.join(filter(None, attr_values.filtered(lambda a: 'Bulb Connection' in a.name).mapped('specification')))
#
# -*- coding: utf-8 -*-

# from odoo import api, fields, models, _
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class OrionSpecification(models.Model):
#     _inherit = 'product.product'
#
#     # Basic fields remain the same
#     calibration = fields.Text('Calibration')
#     capillary = fields.Text('Capillary')
#     bulb_connection = fields.Text('Bulb Connection')
#     diff_temp = fields.Text('Differential Temp')
#     repeatability = fields.Text('Repeatability')
#     other_wetted_parts = fields.Text('Other Wetted Parts')
#     enclosure = fields.Text('Enclosure')
#     pro_cap = fields.Text('Protective Cap')
#     wetted_parts = fields.Text('Wetted Parts')
#     bulletin_no = fields.Text('Bulletin No')
#     model_enhance = fields.Text('Model Enhancements')
#     model_category = fields.Text('Model Category')
#     on_off_diff = fields.Text('On Off Diff')
#     max_pressure_temp = fields.Text('Max Pressure/Temp')
#     photo_jpg = fields.Text('Photo JPG')
#
#     # Computed fields
#     model_name = fields.Text('Model Name', compute='_compute_model', store=True)
#     diaphragm = fields.Text('Diaphragm', compute='_compute_diaphragm', store=True)
#     micro_switch = fields.Text('Micro Switch', compute='_compute_microswitch', store=True)
#     switch_type = fields.Text('Switch Type', compute='_compute_switchtype', store=True)
#     range = fields.Text('Range Code', compute='_compute_rangecode', store=True)
#     range_scale = fields.Text('Range Scale', compute='_compute_rangescale', store=True)
#     pressure_port = fields.Text('Pressure Port', compute='_compute_pressureport', store=True)
#     pressure_housing = fields.Text('Pressure Housing', compute='_compute_pressurehousing', store=True)
#     cable_entry = fields.Text('Cable Entry', compute='_compute_cableentry', store=True)
#     short_name = fields.Text('Short Name', compute='_compute_short_name', store=True)
#     base_type = fields.Text('Base Type', compute='_compute_base_type', store=True)
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_internal_reference(self):
#         for product in self:
#             attr_values = {}
#             for prod in product.product_template_attribute_value_ids:
#                 attr_values[prod.attribute_id.name] = prod.name
#
#             parts = []
#             for field in ["Non Standard Allocation", "Model", "Cable Entry Size",
#                           "Switch Type", "Range Code", "Range Scale", "Microswitch Type",
#                           "Pressure Port", "Pressure housing", "Diaphragm", "Enclosure", "Piston"]:
#                 if field in attr_values:
#                     parts.append(attr_values[field])
#
#             var1 = ' '.join(parts).strip()
#             _logger.debug("Attribute name = %s", var1)
#
#             product.default_code = var1 or product.name
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_short_name(self):
#         for product in self:
#             product.short_name = next(
#                 (pav.name for pav in product.product_template_attribute_value_ids
#                  if pav.attribute_id.name == "Model"),
#                 False
#             )
#
#     def _compute_specification_field(self, attribute_name):
#         """Helper method to compute specification fields based on attribute name"""
#         for product in self:
#             try:
#                 attr_value = product.product_template_attribute_value_ids.filtered(
#                     lambda x: x.attribute_id.name == attribute_name
#                 )
#                 if attr_value:
#                     specification = self.env['product.attribute.value'].search([
#                         ('attribute_id.name', '=', attribute_name),
#                         ('name', '=', attr_value[0].name)  # Add [0] to get first value
#                     ], limit=1).specification  # Add limit=1 to ensure single record
#                     return specification
#             except Exception as e:
#                 _logger.error(f"Error computing {attribute_name}: {str(e)}")
#         return False
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_diaphragm(self):
#         for product in self:
#             product.diaphragm = product._compute_specification_field("Diaphragm")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_microswitch(self):
#         for product in self:
#             product.micro_switch = product._compute_specification_field("Microswitch Type")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_switchtype(self):
#         for product in self:
#             product.switch_type = product._compute_specification_field("Switch Type")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_rangecode(self):
#         for product in self:
#             product.range = product._compute_specification_field("Range Code")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_rangescale(self):
#         for product in self:
#             product.range_scale = product._compute_specification_field("Range Scale")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_pressureport(self):
#         for product in self:
#             product.pressure_port = product._compute_specification_field("Pressure Port")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_pressurehousing(self):
#         for product in self:
#             product.pressure_housing = product._compute_specification_field("Pressure Housing")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_cableentry(self):
#         for product in self:
#             product.cable_entry = product._compute_specification_field("Cable Entry Size")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_pressurehousing(self):
#         for product in self:
#             product.pressure_housing = product._compute_specification_field("Pressure Housing")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_rangescale(self):
#         for product in self:
#             product.range_scale = product._compute_specification_field("Range Scale")
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_base_type(self):
#         for product in self:
#             product.base_type = product._compute_specification_field("Base Type")
# -*- coding: utf-8 -*-

# from odoo import api, fields, models, _
# import logging
#
# _logger = logging.getLogger(__name__)
#
# class OrionSpecification(models.Model):
#     _inherit = 'product.product'
#
#     calibration = fields.Text('Calibration')
#     capillary = fields.Text('Capillary')
#     bulb_connection = fields.Text('Bulb Connection')
#     diff_temp = fields.Text('Differential Temp')
#     repeatability = fields.Text('Repeatability')
#     other_wetted_parts = fields.Text('Other Wetted Parts')
#     enclosure = fields.Text('Enclosure')
#     pro_cap = fields.Text('Protective Cap')
#     wetted_parts = fields.Text('Wetted Parts')
#
#     model_name = fields.Text('Model Name', compute='_compute_model', store=True)
#     diaphragm = fields.Text('Diaphragm', compute='_compute_diaphragm', store=True)
#     micro_switch = fields.Text('Micro Switch', compute='_compute_microswitch', store=True)
#     switch_type = fields.Text('Switch Type', compute='_compute_switchtype', store=True)
#     range = fields.Text('Range Code', compute='_compute_rangecode', store=True)
#     range_scale = fields.Text('Range Scale', compute='_compute_rangescale', store=True)
#     pressure_port = fields.Text('Pressure Port', compute='_compute_pressureport', store=True)
#     pressure_housing = fields.Text('Pressure Housing', compute='_compute_pressurehousing', store=True)
#     cable_entry = fields.Text('Cable Entry', compute='_compute_cableentry', store=True)
#
#     bulletin_no = fields.Text('Bulletin No')
#     short_name = fields.Text('Short Name', compute='_compute_short_name', store=True)
#     model_enhance = fields.Text('Model Enhancements')
#     model_category = fields.Text('Model Category')
#     on_off_diff = fields.Text('On Off Diff')
#     max_pressure_temp = fields.Text('Max Pressure/Temp')
#     photo_jpg = fields.Text('Photo JPG')
#     base_type = fields.Text('Base Type', compute='_compute_base_type', store=True)
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_internal_reference(self):
#         for product in self:
#             attr_values = {}
#             for ptav in product.product_template_attribute_value_ids:
#                 attr_values[ptav.attribute_id.name] = ptav.name
#
#             var1 = ''
#             if "Non Standard Allocation" in attr_values:
#                 var1 += attr_values["Non Standard Allocation"]
#             if "Model" in attr_values:
#                 var1 += attr_values["Model"]
#             if "Cable Entry Size" in attr_values:
#                 var1 += ' ' + attr_values["Cable Entry Size"]
#             if "Switch Type" in attr_values:
#                 var1 += ' ' + attr_values["Switch Type"]
#             if "Range Code" in attr_values:
#                 var1 += ' ' + attr_values["Range Code"]
#             if "Range Scale" in attr_values:
#                 var1 += ' ' + attr_values["Range Scale"]
#             if "Microswitch Type" in attr_values:
#                 var1 += ' ' + attr_values["Microswitch Type"]
#             if "Pressure Port" in attr_values:
#                 var1 += ' ' + attr_values["Pressure Port"]
#             if "Pressure housing" in attr_values:
#                 var1 += ' ' + attr_values["Pressure housing"]
#             if "Diaphragm" in attr_values:
#                 var1 += ' ' + attr_values["Diaphragm"]
#             if "Enclosure" in attr_values:
#                 var1 += ' ' + attr_values["Enclosure"]
#             if "Piston" in attr_values:
#                 var1 += ' ' + attr_values["Piston"]
#
#             _logger.debug("Attribute name = %s", var1)
#
#             if not var1:
#                 var1 = product.name
#             product.default_code = var1
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_short_name(self):
#         for product in self:
#             product.short_name = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Model":
#                     product.short_name = ptav.name
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_model(self):
#         for product in self:
#             product.model_name = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Model":
#                     product.model_name = ptav.product_attribute_value_id.specification
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_diaphragm(self):
#         for product in self:
#             product.diaphragm = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Diaphragm":
#                     product.diaphragm = ptav.product_attribute_value_id.specification
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_microswitch(self):
#         for product in self:
#             product.micro_switch = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Microswitch Type":
#                     product.micro_switch = ptav.product_attribute_value_id.specification
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_switchtype(self):
#         for product in self:
#             product.switch_type = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Switch Type":
#                     product.switch_type = ptav.product_attribute_value_id.specification
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_rangecode(self):
#         for product in self:
#             product.range = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Range Code":
#                     product.range = ptav.product_attribute_value_id.specification
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_pressureport(self):
#         for product in self:
#             product.pressure_port = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Pressure Port":
#                     product.pressure_port = ptav.product_attribute_value_id.specification
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_cableentry(self):
#         for product in self:
#             product.cable_entry = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Cable Entry Size":
#                     product.cable_entry = ptav.product_attribute_value_id.specification
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_pressurehousing(self):
#         for product in self:
#             product.pressure_housing = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Pressure Housing":
#                     product.pressure_housing = ptav.product_attribute_value_id.specification
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_rangescale(self):
#         for product in self:
#             product.range_scale = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Range Scale":
#                     product.range_scale = ptav.product_attribute_value_id.specification
#
#     @api.depends('product_template_attribute_value_ids')
#     def _compute_base_type(self):
#         for product in self:
#             product.base_type = False
#             for ptav in product.product_template_attribute_value_ids:
#                 if ptav.attribute_id.name == "Base Type":
#                     product.base_type = ptav.product_attribute_value_id.specification