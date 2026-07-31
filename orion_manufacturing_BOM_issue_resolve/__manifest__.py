{
    "name": "BOM Issues Resolved",
    "version": "16.0.1.0.0",
    "category": "Manufacturing",
    "summary": "Prevent adding same product multiple times in a BOM",
    "depends": ["mrp"],
    "data": [
        # 'security/ir.model.access.csv',
        # 'views/bom_duplicate_wizard.xml',
        'views/product_filter_bom.xml',
    ],
    "installable": True,
    "application": False,
}
