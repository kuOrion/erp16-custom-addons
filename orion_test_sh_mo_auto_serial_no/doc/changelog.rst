16.0.1 (D. 18 Apr 2025)
------------------------

- initial release

16.0.2 (D. 18 Apr 2025)
------------------------
- [Update] Updated flow for Filter move line

16.0.3 (D. 25 Apr 2025)
------------------------
- [Update] Add MO quantity, Default Parent MO Filter, Inventory overview related point 

16.0.4 (D. 1 May 2025)
------------------------
- [ADD] Added done Quantity count in Internal Transfer Sequence, produce qty field in MO mandatory, source document shows only stock product

16.0.5 (D. 5 May 2025)
------------------------
- [FIX] smart button issue in Picking form view fixed

16.0.6 ( Date : 17 Jul 2026 ) [TICKET/24830]
-----------------------------

[ADD] Admin-only Release and Reassign Serial No on the Manufacturing Order, with automatic reuse of released Serial Numbers (including on completed orders) and a read-only release/reuse history.

16.0.7 ( Date : 20 Jul 2026 ) [TICKET/24830]
-----------------------------

[FIX] Serial No Type now defaults to Type 1 on a new Manufacturing Order.
[FIX] Assign Serial No now uses the updated Prefix immediately after it is changed in Settings, instead of continuing with the old one.
[FIX] Assign Serial No now also appears on the pending Manufacturing Order created after a partial serial assignment (backorder), so remaining quantity can be assigned.

16.0.8 ( Date : 03 Aug 2026 ) [TICKET/24830]
-----------------------------

[FIX] After Release and Reassign, a serial number is no longer linked to the old product in stock (including cross-product reuse); it is associated only with the new product/MO.
[FIX] Sale Delivery remains a standard delivery process: MO, Internal Picking, Start Serial Number and End Serial Number are not shown on Sale Delivery (available on Internal Transfer only).
[FIX] Finished Product quantity and serial number list stay in sync (no extra or missing serials after assign/release/reassign).

16.0.9 ( Date : 19 Aug 2026 ) [TICKET/24830]
-----------------------------

[FIX] Sale Order Delivery now reserves existing serial numbers with standard Odoo Check Availability / Validate. MO, Internal Picking, Start Serial and End Serial remain Internal Transfer only (including reservation).
[FIX] Changing or creating a Serial Number Prefix starts numbering from 1 when no lots already exist for that prefix.
