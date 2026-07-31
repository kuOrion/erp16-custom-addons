from odoo import models, fields, api, _
from datetime import datetime
import json
from collections import OrderedDict
import base64
import logging
from odoo.exceptions import ValidationError, UserError
from decimal import Decimal, ROUND_HALF_UP


_logger = logging.getLogger(__name__)


class AccountEInvoiceCreateJson(models.TransientModel):
    _name = 'account.einvoice.create.json'
    _description = 'Create JSON for selected invoices'

    def get_docdtls(self, invoice):
        """Get document details"""
        dict = OrderedDict()
        dict["Typ"] = "INV"
        dict["No"] = invoice.name
        dict["Dt"] = (invoice.invoice_date or fields.Date.today()).strftime("%d/%m/%Y")
        return dict

    def get_trandtls(self, invoice):
        """Get transaction details"""
        dict = OrderedDict()
        dict["TaxSch"] = "GST"

        # Check if this is an export invoice based on GST Treatment or country
        is_export = False
        gst_treatment = invoice.partner_id.l10n_in_gst_treatment or ""

        if gst_treatment in ["overseas", "special_economic_zone", "deemed_export"]:
            is_export = True
        elif invoice.partner_id.country_id:
            country = invoice.partner_id.country_id.name or ""
            is_export = country.lower() != "india"

        dict["SupTyp"] = "EXPWOP" if is_export else "B2B"
        dict["IgstOnIntra"] = "N"
        dict["RegRev"] = "N"
        dict["EcmGstin"] = None
        return dict

    def get_sellerdtls(self, invoice):
        """Get seller details"""
        dict = OrderedDict()
        gstin = invoice.company_id.vat or ""
        stcd = gstin[:2] if len(gstin) >= 2 else ""

        dict["Gstin"] = gstin
        dict["LglNm"] = invoice.company_id.partner_id.name or ""
        dict["Addr1"] = invoice.company_id.street or ""
        dict["Addr2"] = invoice.company_id.street2 or None
        dict["Loc"] = invoice.company_id.city or ""

        pin_code = invoice.company_id.zip or ""
        if pin_code and pin_code.isdigit():
            dict["Pin"] = int(pin_code)
        else:
            dict["Pin"] = 999999

        dict["Stcd"] = stcd
        dict["Ph"] = None
        dict["Em"] = invoice.company_id.email or None
        return dict

    def get_buyerdtls(self, invoice):
        """Get buyer details"""
        dict = OrderedDict()

        # Check GST treatment first
        gst_treatment = invoice.partner_id.l10n_in_gst_treatment or ""
        is_export = gst_treatment in ["overseas", "special_economic_zone", "deemed_export"]

        if not is_export and invoice.partner_id.country_id:
            country = invoice.partner_id.country_id.name or ""
            is_export = country.lower() != "india"

        # Determine GSTIN
        if not is_export:
            gstin = invoice.partner_id.vat or ""
            if not gstin:
                _logger.warning('Missing GSTIN for Indian partner "%s", using URP', invoice.partner_id.name)
                gstin = "URP"
        else:
            gstin = "URP"

        stcd = gstin[:2] if len(gstin) >= 2 else ""

        dict["Gstin"] = gstin
        dict["LglNm"] = invoice.partner_id.name or ""
        dict["Addr1"] = invoice.partner_id.street or ""
        dict["Addr2"] = invoice.partner_id.street2 or None
        dict["Loc"] = invoice.partner_id.city or "Unknown"

        if dict["Loc"] == "Unknown":
            _logger.warning('City is not set for partner "%s", using default value', invoice.partner_id.name)

        # For export invoices
        if is_export:
            dict["Pos"] = "96"
            dict["Stcd"] = "96"
            dict["Pin"] = 999999
        else:
            dict["Pos"] = stcd
            dict["Stcd"] = stcd
            pin_code = invoice.partner_id.zip or ""
            if pin_code and pin_code.isdigit():
                dict["Pin"] = int(pin_code)
            else:
                _logger.warning('Invalid PIN code for partner "%s", using default', invoice.partner_id.name)
                dict["Pin"] = 999999

        dict["Ph"] = None
        dict["Em"] = None
        return dict



    def get_shippingdtls(self, invoice):
        """Get shipping details"""

        if not invoice.partner_shipping_id:
            return None

        partner = invoice.partner_shipping_id

        # -------------------------
        # City Validation
        # -------------------------
        if not partner.city:
            raise ValidationError(
                _('Error - City is not set in the Address of "%s"') % (partner.name)
            )

        # -------------------------
        # Zipcode Validation
        # -------------------------
        if not partner.zip:
            raise ValidationError(
                _('Error - Zipcode is not set in the Address of "%s"') % (partner.name)
            )

        # Remove spaces from zipcode for validation
        zipcode = partner.zip.strip()

        # Check zipcode contains only digits
        if not zipcode.isdigit():
            raise ValidationError(
                _('Error - Invalid Zipcode in the Address of "%s". Zipcode must contain only numbers without spaces.') % (
                    partner.name)
            )

        dict = OrderedDict()

        # Check if shipping is to export location
        is_export = False
        if partner.country_id:
            country = partner.country_id.name or ""
            is_export = country.lower() != "india"

        gstin = partner.vat or "URP"
        stcd = gstin[:2] if len(gstin) >= 2 else ""

        dict["Gstin"] = gstin
        dict["LglNm"] = partner.name or ""
        dict["Addr1"] = partner.street or ""
        dict["Addr2"] = partner.street2 or None
        dict["Loc"] = partner.city

        dict["Pin"] = int(zipcode)

        dict["Stcd"] = "96" if is_export else stcd

        return dict
    def get_refdtls(self, invoice):
        """Get reference details"""
        dict = OrderedDict()
        dict["InvRm"] = "NICGEPP"
        return dict

    def get_unit(self, unit):
        """Convert Odoo units to GST standard units"""
        unit_mapping = {
            "Cubic Meter(s)": "CBM",
            "Cubic Meters": "CBM",
            "Kg(s)": "KGS",
            "kg": "KGS",
            "Liter(s)": "LTR",
            "Liters": "LTR",
            "meter(s)": "MTR",
            "meter": "MTR",
            "Unit(s)": "NOS",
            "Units": "NOS",
            "NOS": "NOS",
            "UNT": "NOS",
            "Box": "BOX",
            "Piece": "PCS",
            "Pieces": "PCS",
            "Hour": "HUR",
            "Hours": "HUR",
        }

        return unit_mapping.get(unit, "OTH")

    def is_export_invoice(self, invoice):
        """Check if invoice is for export"""
        # Check GST treatment first (Odoo 16 field)
        gst_treatment = invoice.partner_id.l10n_in_gst_treatment or ""
        if gst_treatment in ["overseas", "special_economic_zone", "deemed_export"]:
            return True

        # Check country
        if invoice.partner_id.country_id:
            country = invoice.partner_id.country_id.name or ""
            return country.lower() != "india"

        return False

    def get_tax_details(self, invoice):
        """
        Get comprehensive tax details from invoice
        For export invoices, always return 0 tax regardless of what's in Odoo
        """
        is_export = self.is_export_invoice(invoice)

        # FOR EXPORT INVOICES: Always return 0 tax
        if is_export:
            return {
                "CGST": 0.0,
                "SGST": 0.0,
                "IGST": 0.0,
                "CGST_PER": 0.0,
                "SGST_PER": 0.0,
                "IGST_PER": 0.0,
                "is_export": True
            }

        # For domestic invoices, calculate actual taxes
        tax_data = {
            "CGST": 0.0,
            "SGST": 0.0,
            "IGST": 0.0,
            "CGST_PER": 0.0,
            "SGST_PER": 0.0,
            "IGST_PER": 0.0,
            "is_export": False
        }

        # Get all tax lines from the invoice
        tax_lines = invoice.line_ids.filtered(lambda l: l.tax_line_id)

        for line in tax_lines:
            tax = line.tax_line_id
            tax_name = (tax.name or "").upper()
            tax_amount = abs(line.balance)
            tax_percent = tax.amount

            # Identify GST type
            if "CGST" in tax_name or "CENTRAL" in tax_name:
                tax_data["CGST"] += tax_amount
                if tax_percent > tax_data["CGST_PER"]:
                    tax_data["CGST_PER"] = tax_percent

            elif "SGST" in tax_name or "STATE" in tax_name:
                tax_data["SGST"] += tax_amount
                if tax_percent > tax_data["SGST_PER"]:
                    tax_data["SGST_PER"] = tax_percent

            elif "IGST" in tax_name or "INTEGRATED" in tax_name:
                tax_data["IGST"] += tax_amount
                if tax_percent > tax_data["IGST_PER"]:
                    tax_data["IGST_PER"] = tax_percent

        # If no tax lines found, compute from invoice lines
        if not tax_lines:
            _logger.info('Computing taxes from invoice lines for %s', invoice.name)

            for line in invoice.invoice_line_ids:
                if line.display_type in ('line_section', 'line_note') or not line.tax_ids:
                    continue

                # Compute taxes for this line
                taxes_res = line.tax_ids.compute_all(
                    line.price_unit * (1 - (line.discount or 0.0) / 100.0),
                    currency=invoice.currency_id,
                    quantity=line.quantity,
                    product=line.product_id,
                    partner=invoice.partner_id
                )

                for tax in taxes_res['taxes']:
                    tax_rec = self.env['account.tax'].browse(tax['id'])
                    tax_name = (tax_rec.name or "").upper()
                    tax_amount = tax['amount']
                    tax_percent = tax_rec.amount

                    if "CGST" in tax_name or "CENTRAL" in tax_name:
                        tax_data["CGST"] += tax_amount
                        if tax_percent > tax_data["CGST_PER"]:
                            tax_data["CGST_PER"] = tax_percent

                    elif "SGST" in tax_name or "STATE" in tax_name:
                        tax_data["SGST"] += tax_amount
                        if tax_percent > tax_data["SGST_PER"]:
                            tax_data["SGST_PER"] = tax_percent

                    elif "IGST" in tax_name or "INTEGRATED" in tax_name:
                        tax_data["IGST"] += tax_amount
                        if tax_percent > tax_data["IGST_PER"]:
                            tax_data["IGST_PER"] = tax_percent

        # Round values
        tax_data["CGST"] = round(tax_data["CGST"], 2)
        tax_data["SGST"] = round(tax_data["SGST"], 2)
        tax_data["IGST"] = round(tax_data["IGST"], 2)

        return tax_data

    def get_line_tax_details(self, invoice, line):
        """
        Get tax details for a specific invoice line
        For export invoices, always return 0 tax
        """
        is_export = self.is_export_invoice(invoice)

        line_tax = {
            "CGST": 0.0,
            "SGST": 0.0,
            "IGST": 0.0,
            "CGST_PER": 0.0,
            "SGST_PER": 0.0,
            "IGST_PER": 0.0,
        }

        # FOR EXPORT INVOICES: Always return 0 tax
        if is_export:
            return line_tax

        if not line.tax_ids:
            return line_tax

        # Compute taxes for this line (only for domestic invoices)
        taxes_res = line.tax_ids.compute_all(
            line.price_unit * (1 - (line.discount or 0.0) / 100.0),
            currency=invoice.currency_id,
            quantity=line.quantity,
            product=line.product_id,
            partner=invoice.partner_id
        )

        for tax in taxes_res['taxes']:
            tax_rec = self.env['account.tax'].browse(tax['id'])
            tax_name = (tax_rec.name or "").upper()
            tax_amount = tax['amount']
            tax_percent = tax_rec.amount

            if "CGST" in tax_name or "CENTRAL" in tax_name:
                line_tax["CGST"] = tax_amount
                line_tax["CGST_PER"] = tax_percent

            elif "SGST" in tax_name or "STATE" in tax_name:
                line_tax["SGST"] = tax_amount
                line_tax["SGST_PER"] = tax_percent

            elif "IGST" in tax_name or "INTEGRATED" in tax_name:
                line_tax["IGST"] = tax_amount
                line_tax["IGST_PER"] = tax_percent

        return line_tax



    def round_value(self, value):
        """Round value using HALF_UP (25.50 -> 26, 25.49 -> 25)."""
        return float(
            Decimal(str(value)).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP
            )
        )

    def get_valdtls(self, invoice, taxlist):
        dict = OrderedDict()

        dict["AssVal"] = self.round_value(invoice.amount_untaxed)
        dict["CgstVal"] = self.round_value(taxlist["CGST"])
        dict["SgstVal"] = self.round_value(taxlist["SGST"])
        dict["IgstVal"] = self.round_value(taxlist["IGST"])
        dict["CesVal"] = 0
        dict["StCesVal"] = 0
        dict["Discount"] = 0

        dict["RndOffAmt"] = 0.0
        dict["TotInvVal"] = self.round_value(invoice.amount_total)

        return dict

    def convert_to_company_currency(self, invoice, amount):
        """
        Convert an amount from invoice currency to company currency (INR).
        If invoice is already in company currency, return the original amount.
        """
        if invoice.currency_id == invoice.company_currency_id:
            return round(amount, 2)

        return round(
            invoice.currency_id._convert(
                amount,
                invoice.company_currency_id,
                invoice.company_id,
                invoice.invoice_date or fields.Date.today(),
            ),
            2
        )



    # def get_valdtls_export(self, invoice):
    #     """Get value details for export invoices in INR"""
    #
    #     dict = OrderedDict()
    #
    #     ass_val = self.convert_to_company_currency(
    #         invoice,
    #         invoice.amount_untaxed
    #     )
    #
    #     tot_val = self.convert_to_company_currency(
    #         invoice,
    #         invoice.amount_total
    #     )
    #
    #     # Calculate total discount amount
    #     total_discount = 0.0
    #     for line in invoice.invoice_line_ids.filtered(lambda l: not l.display_type):
    #         discount = (
    #                 line.price_unit
    #                 * line.quantity
    #                 * (line.discount or 0.0)
    #                 / 100.0
    #         )
    #
    #         total_discount += self.convert_to_company_currency(
    #             invoice,
    #             discount
    #         )
    #
    #     dict["AssVal"] = self.round_value(ass_val)
    #     dict["CgstVal"] = 0
    #     dict["SgstVal"] = 0
    #     dict["IgstVal"] = 0
    #     dict["CesVal"] = 0
    #     dict["StCesVal"] = 0
    #
    #     # Discount Amount
    #     dict["Discount"] = self.round_value(total_discount)
    #
    #     dict["RndOffAmt"] = 0
    #     dict["TotInvVal"] = self.round_value(tot_val)
    #
    #     return dict

    def get_valdtls_export(self, invoice):
        dict = OrderedDict()

        ass_val = self.convert_to_company_currency(
            invoice,
            invoice.amount_untaxed
        )

        tot_val = self.convert_to_company_currency(
            invoice,
            invoice.amount_total
        )

        total_discount = 0.0
        for line in invoice.invoice_line_ids.filtered(lambda l: not l.display_type):
            discount = (
                    line.price_unit
                    * line.quantity
                    * (line.discount or 0.0)
                    / 100.0
            )
            total_discount += self.convert_to_company_currency(invoice, discount)

        dict["AssVal"] = round(ass_val, 2)
        dict["CgstVal"] = 0
        dict["SgstVal"] = 0
        dict["IgstVal"] = 0
        dict["CesVal"] = 0
        dict["StCesVal"] = 0
        dict["Discount"] = round(total_discount, 2)
        dict["RndOffAmt"] = 0
        dict["TotInvVal"] = round(tot_val, 2)

        return dict





    def get_itemlist(self, invoice, taxlist):
        """Get item list - monetary values in Company Currency (INR)"""
        itemlist = []
        srno = 1
        is_export = taxlist.get("is_export", False)

        for line in invoice.invoice_line_ids:

            if line.display_type in ('line_section', 'line_note'):
                continue

            dict = OrderedDict()
            dict["SlNo"] = str(srno)

            # Product Description
            if line.product_id:
                product_name = line.product_id.name or ""
                if line.product_id.default_code:
                    product_name = f"{product_name} {line.product_id.default_code}"
                dict["PrdDesc"] = product_name or line.name
            else:
                dict["PrdDesc"] = line.name

            # Service/Product
            if line.product_id:
                dict["IsServc"] = "Y" if line.product_id.type == "service" else "N"
            else:
                dict["IsServc"] = "Y"

            # HSN Code
            hsn_code = ""
            if line.product_id:
                hsn_fields = ['l10n_in_hsn_code', 'hsn_code', 'x_hsn_code']
                for field in hsn_fields:
                    if hasattr(line.product_id, field):
                        hsn_code = getattr(line.product_id, field) or ""
                        if hsn_code:
                            break

            if not hsn_code:
                _logger.warning(
                    'Missing HSN code for "%s", using default',
                    line.product_id.name if line.product_id else line.name
                )
                hsn_code = "99999999"

            dict["HsnCd"] = hsn_code

            # Quantity
            dict["Qty"] = round(line.quantity, 2)
            dict["FreeQty"] = 0
            dict["Unit"] = self.get_unit(line.product_uom_id.name) if line.product_uom_id else "OTH"

            # ----------------------------------------------------
            # Convert Monetary Values to INR
            # ----------------------------------------------------

            unit_price = self.convert_to_company_currency(
                invoice,
                line.price_unit
            )

            subtotal = self.convert_to_company_currency(
                invoice,
                line.price_subtotal
            )

            dict["UnitPrice"] = unit_price
            dict["TotAmt"] = subtotal


            discount_amount = (
                    line.price_unit *
                    line.quantity *
                    (line.discount or 0.0) / 100.0
            )

            discount_amount = self.convert_to_company_currency(
                invoice,
                discount_amount
            )

            # Always send 0 in JSON
            dict["Discount"] = 0

            dict["PreTaxVal"] = 0
            dict["AssAmt"] = subtotal

            # ----------------------------------------------------
            # Tax Details
            # ----------------------------------------------------

            line_tax = self.get_line_tax_details(invoice, line)

            if is_export:

                dict["GstRt"] = 0
                dict["IgstAmt"] = 0
                dict["CgstAmt"] = 0
                dict["SgstAmt"] = 0
                dict["TotItemVal"] = subtotal

            else:

                if line_tax["IGST_PER"] > 0:
                    gst_rate = line_tax["IGST_PER"]
                elif line_tax["CGST_PER"] > 0 or line_tax["SGST_PER"] > 0:
                    gst_rate = line_tax["CGST_PER"] + line_tax["SGST_PER"]
                elif taxlist["IGST_PER"] > 0:
                    gst_rate = taxlist["IGST_PER"]
                else:
                    gst_rate = taxlist["CGST_PER"] + taxlist["SGST_PER"]

                dict["GstRt"] = round(gst_rate, 2)

                cgst = self.convert_to_company_currency(
                    invoice,
                    line_tax["CGST"]
                )

                sgst = self.convert_to_company_currency(
                    invoice,
                    line_tax["SGST"]
                )

                igst = self.convert_to_company_currency(
                    invoice,
                    line_tax["IGST"]
                )

                dict["CgstAmt"] = cgst
                dict["SgstAmt"] = sgst
                dict["IgstAmt"] = igst

                dict["TotItemVal"] = round(
                    subtotal + cgst + sgst + igst,
                    2
                )

            # Other Charges
            dict["CesRt"] = 0
            dict["CesAmt"] = 0
            dict["CesNonAdvlAmt"] = 0
            dict["StateCesRt"] = 0
            dict["StateCesAmt"] = 0
            dict["StateCesNonAdvlAmt"] = 0
            dict["OthChrg"] = 0

            itemlist.append(dict)
            srno += 1

        return itemlist

    def create_json_file(self):
        """Main method to create JSON file for selected invoices"""
        date_string = datetime.now().strftime("%d-%m-%Y")
        report_name = 'invoice_to_json'
        filename = f'{report_name}_{date_string}.json'

        active_ids = self._context.get('active_ids', [])

        if not active_ids:
            raise UserError(_('No invoices selected. Please select at least one invoice.'))

        # Validate and filter invoices
        invoices = self.env['account.move'].browse(active_ids).filtered(
            lambda inv: inv.move_type == 'out_invoice' and inv.state == 'posted'
        )

        if not invoices:
            raise UserError(_('No valid posted customer invoices found in selection.'))

        invlist = []
        for invoice in invoices:
            # Get tax details (this now handles export vs domestic)
            taxlist = self.get_tax_details(invoice)
            is_export = taxlist.get("is_export", False)

            # Get all required details
            docdtls = self.get_docdtls(invoice)
            trandtls = self.get_trandtls(invoice)
            sellerdtls = self.get_sellerdtls(invoice)
            buyerdtls = self.get_buyerdtls(invoice)
            shippingdtls = self.get_shippingdtls(invoice)
            refdtls = self.get_refdtls(invoice)

            # Get items list
            itemlist = self.get_itemlist(invoice, taxlist)

            # Get value details based on invoice type
            if is_export:
                valdtls = self.get_valdtls_export(invoice)
            else:
                valdtls = self.get_valdtls(invoice, taxlist)

            # Build invoice JSON structure
            invoice_dict = OrderedDict()
            invoice_dict["Version"] = "1.1"
            invoice_dict["TranDtls"] = trandtls
            invoice_dict["DocDtls"] = docdtls
            invoice_dict["SellerDtls"] = sellerdtls
            invoice_dict["BuyerDtls"] = buyerdtls

            if shippingdtls:
                invoice_dict["ShipDtls"] = shippingdtls

            invoice_dict["ValDtls"] = valdtls
            invoice_dict["RefDtls"] = refdtls
            invoice_dict["ItemList"] = itemlist

            invlist.append(invoice_dict)

        if not invlist:
            raise UserError(_('No valid invoices found to process'))

        # Create JSON file
        json_data = json.dumps(invlist, indent=2, sort_keys=False)

        # Create attachment
        attachment_vals = {
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(json_data.encode('utf-8')),
            'mimetype': 'application/json',
            'res_model': 'account.move',
            'res_id': invoices[0].id if invoices else False,
        }

        attachment = self.env['ir.attachment'].sudo().create(attachment_vals)

        _logger.info('E-Invoice JSON created successfully with %d invoices', len(invlist))

        # Return action to download the file
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
