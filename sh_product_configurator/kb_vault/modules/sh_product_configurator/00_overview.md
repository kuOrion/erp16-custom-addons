# Product Configurator — Overview
Status: [ACTIVE]
Version: 16.0.12
Last Updated: 2026-07-14

## Purpose
Kaustubha Udyog's manufacturing catalog needs products where attributes form a **hierarchy** (an attribute's available choices depend on what was picked for a parent attribute), variants must be created **manually** (not auto-exploded on every possible combination), and each variant needs an **auto-generated internal reference** built from its selected attribute values. Standard Odoo `product.attribute` / `product.template.attribute.line` has no parent/child concept and always eagerly creates variants for dynamic attributes.

## What It Achieves
- Nested/dependent attributes: an attribute can declare a parent attribute + parent value (`sh_parent_attribute`, `sh_parent_value`); child attributes only make sense once a specific parent value is chosen. Enforced both in backend attribute records and in the website/sale configurator's child-attribute show/hide JS.
- Attributes and values become **product-specific** (`sh_product_tmpl_id` on `product.attribute`), not shared master data — one attribute line = one attribute per template, enforced by a uniqueness constraint.
- Variant explosion is disabled for the template form: `_create_variant_ids` is overridden to skip the "push single value onto existing empty variant" step, so adding a dynamic attribute never silently mutates the blank starter variant. Variants are instead created explicitly through the variant (`product.product`) form via `product_template_id` + a chosen attribute combination.
- Only System Administrators (`base.group_system`) can create attributes, attribute values, attribute lines, or products/variants — this is a deliberate lockdown, not an oversight.
- Auto-generated `default_code` (internal reference) built by concatenating truncated attribute value names, skipping any child attribute whose parent-value condition is already implied by the parent's own value (avoids redundant codes). Company-configurable via digit count and separator settings.
- Duplicating a product template copies attributes/hierarchy/BOMs but deliberately creates **zero variants** on the copy — the user must recreate variants manually, matching the "manual variant creation" philosophy.
- A read-only "Specification" tab on the variant form auto-lists attribute name/description pairs, plus a separate free-text "Extra Specification" table for manually entered info not tied to any attribute.
- Custom Odoo Sales product configurator modal (website/backend) is patched so it also handles `product.product` model context (not just `sale.order.line`), lets users edit an existing variant's attributes in place, and dynamically hides/shows child attribute groups based on parent selection.

## Key Concepts
- **PTAV** = `product.template.attribute.value`, standard Odoo model linking a template, an attribute, and a specific attribute value.
- **Parent/child attribute hierarchy**: lives on `product.attribute` (`sh_parent_attribute`, `sh_parent_value`) and mirrored on `product.template.attribute.line` (`parent_attribute_value_id`, pointing to the PTAV that must be selected for the child line to be relevant). Attributes with a parent are auto-flagged `sh_is_custom_attribute=True`.
- **Dynamic attributes only**: `create_variant` defaults to `'dynamic'` on every attribute — variants are never pre-created for every combination; they exist only once a user explicitly makes one.
- **Manual variant creation**: creating a `product.product` record with `product_template_id` set binds it to that template's combination and flags `sh_is_created_manually=True`; `sh_is_record_saved` distinguishes a "real" saved variant from a transient placeholder the configurator UI creates/destroys during editing.
- **Internal reference (default_code) generation**: company settings `sh_product_int_ref_gen` (feature toggle), `sh_pdt_attr_digit` (chars per attribute value to include), `sh_pdt_seq_sep` / `sh_pdt_new_seq_sep` (separators for existing vs. newly generated codes).
- **Duplicate-name guard**: product template/variant names must be unique; names starting with `N` (case-insensitive) bypass the uniqueness check and BOM-copy-on-duplicate logic treats them specially (see [[09_known_issues]]).

## Module Map
[[01_architecture]] | [[02_data_flow]] | [[03_models]] | [[04_views_xml]] | [[05_owl_components]] | [[06_controllers]] | [[07_csv_data]] | [[08_dependencies]] | [[09_known_issues]]
