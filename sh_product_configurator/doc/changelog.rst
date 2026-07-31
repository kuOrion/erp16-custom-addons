16.0.1 
------

Initial Release

16.0.2 ( Date : 26 November 2025 ) [TICKET/24830]
-------------------------------------------------

[Add] Specification and Attribute Flow in Product Configurator Customization. [Kaustubha Udyog SO20310]

( Date : 04 December 2024 ) [TICKET/24830]
-------------------------------------------------

[Fix] 7 bugs fixed.

( Date : 05 December 2024 ) [TICKET/24830]
------------------------------------------

[Fix] Description bugs fixed.

16.0.3 ( Date : 22 December 2025 ) [BUG10044, BUG10045, BUG10046, BUG10047]
---------------------------------------------------------------------------

[Fix] Bug of Don't want child Attribute count on internal reference Generation logic in product. Default not selected any attribute. Old selected record remove on edit product configurator customization.

( Date : 23 December 2025 ) [BUG10044, BUG10045, BUG10130, BUG10134]
--------------------------------------------------------------------

[Fix] Bug of one attribute display in product variant.

16.0.4 ( Date : 29 January 2026 ) 
---------------------------------

[Add] CR 1. Sequence handler: Implemented a sequence handler for attributes, allowing reordering through a dedicated widget.
         2. Internal reference and duplication: Developed logic for handling product duplication and variant creation based on internal references starting
         3. Child attributes and parent linking: Implemented automatic linking of child attributes to their parent attribute and value, ensuring sh_parent_attribute and sh_parent_value are
           populated, and restricted selection to new attributes/values when using the 'Sub-Attributes' feature.

( Date : 06 February 2026 ) [BUG11149, BUG11150, BUG11154, BUG11155, BUG11156, BUG11157]
----------------------------------------------------------------------------------------

[Fix] Bugs.

16.0.5 ( Date : 09 February 2026 ) [BUG11282]
---------------------------------------------

[Fix] Atrribute Creation issue.

16.0.6 ( Date : 23 February 2026 ) [BUG11585]
----------------------------------

[Fix] Added sequence logic for newly created child attributes to display them right after their parent attribute or at the end of the list.

16.0.7 ( Date : 24 February 2026 ) [BUG11584]
----------------------------------

[Fix] Resolved an issue where product duplication would fail if a product template had no variants or if the internal reference was defined directly on the template instead of its variants.

16.0.8 ( Date : 18 March 2026 ) [BUG12107,12108]
------------------------------------------------

[Add] DFS-Based Resequencer and Advanced Product Duplication.

16.0.9 ( Date : 19 March 2026 ) [BUG12140]
------------------------------------------

[Fix] Issue For Sequence Handler.

16.0.10 ( Date : 01 April 2026 )
--------------------------------

[Add] On duplicated product templates, prevent renaming to an already existing product name after removing "(copy)", and copy related BOMs when the source product name starts with "N".

16.0.11 ( Date : 11 April 2026 )
--------------------------------

[Fix] Prevent adding '(copy)' to product name if it starts with 'N' during duplication.
[Fix] Ensure BoM and variant extra data (specifications, custom template links) are copied for all products during duplication.


( Date : 13 April 2026 )
------------------------

[Fix] BOM not Copy on Duplicate.
[Fix] Allow to make dublicate name without N Prefix.

( Date : 14 April 2026 )
------------------------

[Remove] BOM variant creation and variant creation warning.
[Fix] Existing product not checked issue.

( Date : 21 April 2026 )
------------------------

[Fix] Restrict manual variant/product creation when a product template with the same name already exists.
[Fix] Remove temporary side-effect variant records on discard and avoid duplicate combination conflicts in variant flow.

( Date : 22 April 2026 )
------------------------

[Fix] Product variant creation after new product save then add attribute issue fix.

( Date : 23 April 2026 )
------------------------

[Fix] Prevent variant auto-creation on product duplication; BOMs are copied at template level only (variant-specific BOMs no longer create duplicate variants).

16.0.12 ( Date : 17 July 2026 )
-------------------------------

[Add] Product names starting with "R" are now also allowed to duplicate without renaming, same as the existing "N" prefix behavior.
