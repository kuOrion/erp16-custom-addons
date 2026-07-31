# Models
Status: [ACTIVE]
Back to [[00_overview]]

## ProductAttribute (product.attribute) — inherit
File: `models/product_attribute.py`
Status: [ACTIVE]
Purpose: Adds parent/child hierarchy metadata and per-template scoping to attributes.
Key Fields:
- `sh_parent_attribute` (Many2one product.attribute) — the attribute this one depends on
- `sh_parent_value` (Many2one product.attribute.value, domain scoped to `sh_parent_attribute`) — required parent value for this attribute to apply
- `sh_product_tmpl_id` (Many2one product.template, readonly) — which template this attribute belongs to (attributes are not shared master data here)
- `sh_is_custom_attribute` (Boolean) — true for any attribute created as a child/sub-attribute
- `create_variant` defaults to `'dynamic'`
Critical Methods:
- `create()` — requires `base.group_system`; if parent info isn't already in vals, pulls the parent PTAV from `context['active_id']` (used when creating a sub-attribute from a PTAV's "Sub-Attributes" one2many) and stamps `sh_parent_value`/`sh_parent_attribute`/`sh_is_custom_attribute`/`sh_product_tmpl_id`.
See also: [[02_data_flow#Flow 1]]

## ProductAttributeValue (product.attribute.value) — inherit
File: `models/product_attribute.py`
Status: [ACTIVE]
Purpose: Adds a free-text description; locks creation to admins.
Key Fields: `description` (Char)
Critical Methods: `create()` — requires `base.group_system`.

## ProductTemplate (product.template) — inherit
File: `models/product_template.py`
Status: [ACTIVE]
Purpose: Enforces unique product names (with an `N`-prefix bypass), disables auto variant explosion, and rebuilds attribute hierarchy correctly on duplicate.
Key Fields: `sh_is_duplicated_template` (Boolean, copy=False) — technical flag marking a just-duplicated record so a rename validation exemption applies once.
Critical Methods:
- `_should_skip_duplicate_name_validation(name)` — [CHANGED: v16.0.12] True if name (stripped) starts with `N` or `R` (case-insensitive). Names starting with either prefix skip the uniqueness check entirely — deliberate business rule, not a bug (see [[09_known_issues]]). > Previously: only `N` was recognized — see [[changelog/v16.0.12]]
- `create()` — requires `base.group_system`; runs `_validate_unique_product_name` unless `create_product_product` context is set (i.e. name check is deferred to the variant-create path in that flow) or the name is exempt.
- `write()` — re-validates uniqueness on rename (excluding self); if the renamed record was `sh_is_duplicated_template`, clears that flag afterward via a context-guarded recursive `write()`.
- `_create_variant_ids()` — **overridden, not calling super()**. Reimplements the standard method but **skips** the block that pushes newly-added single-value attributes onto every pre-existing empty variant. Rationale: attributes here are always dynamic, so a freshly added attribute should never silently "configure" the blank starter variant — variants must be made explicitly. Honors `sh_skip_variant_creation` context (used during duplicate) to no-op entirely. The old standard-behavior version is left commented out in the file for reference.
- `copy()` — see [[02_data_flow#Flow 5]] for the full multi-step rebuild of attributes/hierarchy/BOMs; sets `sh_skip_variant_creation` context so the copy always starts with zero variants.
- `_get_variant_match_key`, `_get_matching_duplicate_combination`, `_get_or_create_duplicate_variant` — helpers for matching old variants to equivalent new-template combinations by attribute+value **name** (not id, since duplicated attributes get new ids). Currently only exercised indirectly; primary duplicate flow does not auto-create variants.
- `_copy_duplicate_boms(new_template)` — copies every `mrp.bom` with `product_tmpl_id=self` onto the new template as a template-level BOM (`product_id=False`); variant-specific BOM links are intentionally dropped.
- `_copy_variant_extra_data(new_template)` — copies `sh_extra_spec_line_ids` and preserves `product_template_id` cross-links for any matching variants (no-op today since duplicates have 0 variants).
See also: [[02_data_flow#Flow 5]], [[09_known_issues]]

## ProductTemplateAttributeLine (product.template.attribute.line) — inherit
File: `models/product_template_attribute_line.py`, `_order = "sequence, id"`
Status: [ACTIVE]
Purpose: Encodes the hierarchy edge (which PTAV a line depends on) and keeps display order consistent with that hierarchy.
Key Fields:
- `parent_attribute_value_id` (Many2one product.template.attribute.value, index=True, ondelete='cascade') — the specific PTAV that must be selected for this line to be relevant
- `sequence` (Integer, default=999) — new lines sort to the bottom by default
Critical Methods:
- `_check_duplicate_attribute_name_per_template()` (`@api.constrains`) — blocks two lines on one template sharing an attribute name (case-insensitive lookup, then exact-match filter).
- `_onchange_attribute_id_check_duplicate()` — UI-time duplicate check; reverts/clears the field and deletes the just-created attribute if it turns out to be an unused duplicate (so users don't accumulate orphan attribute records from typos).
- `_sh_resequence_hierarchical()` — full DFS-based global resequence of all lines for affected templates (used historically; see BUG12107/12108 in changelog). Honors `sh_skip_resequence` context.
- `_get_all_descendant_ids(line, all_template_lines)` — recursive helper collecting a line's full subtree.
- `_sh_insert_hierarchically()` — targeted, minimal-movement insertion: places a line right after the last existing descendant of its parent, shifting only the lines that would otherwise collide. Preferred over the full resequence for normal inserts (less disruptive to manual ordering).
- `create()` — requires `base.group_system`; auto-fills `product_tmpl_id` from the parent PTAV; forces `sequence=999` for genuinely new lines (skips this if `sh_keep_sequence` context is set, used during template `copy()`); if the attribute itself is being created inline as a child, stamps hierarchy fields onto its vals; calls `_sh_insert_hierarchically()` afterward unless `sh_skip_resequence`.
- `write()` — only triggers `_sh_insert_hierarchically()` when `parent_attribute_value_id` changes (not on manual `sequence` drags, so drag-and-drop reordering persists undisturbed).
See also: [[02_data_flow#Flow 1]]

## ProductTemplateAttributeValue (product.template.attribute.value) — inherit
File: `models/product_template_attribute_value.py`
Status: [ACTIVE]
Purpose: Lets a PTAV declare sub-attribute lines (child attributes gated on this specific value) and keeps those children's `product.attribute` metadata in sync.
Key Fields:
- `child_attribute_line_ids` (One2many product.template.attribute.line via `parent_attribute_value_id`) — "Sub-Attributes" shown on the PTAV form
- `description` (Char, related to `product_attribute_value_id.description`, store=True)
Critical Methods:
- `create()` — requires `base.group_system`; calls `_sync_child_attributes()` after creation.
- `write()` — calls `_sync_child_attributes()` whenever `child_attribute_line_ids` or effectively any field changes (broad `any(field in vals for field in self._fields)` check — see [[09_known_issues]] for cost concern).
- `_sync_child_attributes()` — for each child line's attribute, pushes `sh_parent_attribute`/`sh_parent_value`/`sh_product_tmpl_id`/`sh_is_custom_attribute=True` onto that attribute if not already matching. Keeps the `product.attribute` hierarchy fields consistent even if a child was linked outside the normal create flow.
See also: [[02_data_flow#Flow 1]]

## ProductProduct (product.product) — inherit (models/product_product.py)
Status: [ACTIVE]
Purpose: Core variant-creation guard rails — manual binding to a template, duplicate-combination prevention, and internal reference (default_code) generation.
Key Fields:
- `product_template_id` (Many2one product.template) — the custom "pick a template" field used by the manual variant-creation UI; distinct from standard `product_tmpl_id` and synced into it on save
- `product_no_variant_attribute_value_ids`, `product_custom_attribute_value_ids` — recomputed/filtered to only PTAVs still valid for the (possibly changed) template
- `product_template_variant_value_ids` — domain widened to `[]` (standard Odoo restricts to `attribute_line_id.value_count > 1`; this module needs single-value lines selectable too)
- `show_product_template_field` (compute) — True only when the variant has no `product_template_variant_value_ids` yet (i.e. still an "empty starter" variant)
- `sh_is_created_manually`, `sh_is_record_saved` (Boolean) — see [[00_overview#Key Concepts]]
Critical Methods:
- `_custom_default_code()` — builds `default_code` from `product_template_attribute_value_ids`, using company settings `sh_pdt_seq_sep`/`sh_pdt_attr_digit`, skipping attribute values whose parent-value condition is already satisfied (see [[02_data_flow#Flow 3]]).
- `create()` — requires `base.group_system`; blocks creating a duplicate-named template implicitly when `create_product_product` context + a bare `name` is given; auto-binds `product_tmpl_id` from `product_template_id`; stamps `sh_is_created_manually`/`sh_is_record_saved`; after `super().create()`, regenerates `default_code` per variant if `sh_product_int_ref_gen` is on.
- `write()` — the most complex method in the module: (1) if `product_template_attribute_value_ids` changes and `sh_skip_product_template_sync` isn't set, computes the resulting combination per record, deletes **temporary/unsaved** duplicate variants one-by-one to dodge the DB unique constraint, then raises `UserError` if a **real** duplicate remains; (2) syncs `product_template_id` → `product_tmpl_id`, again with a duplicate-combination guard that hard-deletes side-effect variants and commits before raising; (3) archives the old template if a variant's `product_template_id` link changed; (4) regenerates `default_code` if the combination or `force_update_default_code` changed.
- `_compute_custom_attribute_values()` / `_compute_no_variant_attribute_values()` — prune stale PTAV references that no longer belong to the variant's (possibly changed) template.
See also: [[02_data_flow#Flow 3]], [[09_known_issues]]

## ProductAttributeCustomValue (product.attribute.custom.value) — inherit
File: `models/product_product.py`
Status: [ACTIVE]
Purpose: Links a custom attribute value entry back to the `product.product` (sale order line values reused here).
Key Fields: `sh_product_id` (Many2one product.product, ondelete='cascade')

## ShProductSpecification — sh.product.variant.spec.line / sh.product.variant.extra.line / ProductProduct spec mixin
File: `models/sh_product_specification.py`
Status: [ACTIVE]
Purpose: Read-only auto-generated spec table (from attributes) plus a free-editable extra-spec table, both shown on the variant form.
Key Fields:
- `sh.product.variant.spec.line`: `sh_product_id`, `sh_name` (attribute name), `sh_value` (attribute value description)
- `sh.product.variant.extra.line`: `sh_product_id`, `sh_name`, `sh_value` (fully manual, no compute)
- `product.product.sh_spec_line_ids` (One2many, compute, store=True) — auto spec
- `product.product.sh_extra_spec_line_ids` (One2many) — manual spec
Critical Methods:
- `_compute_sh_spec_lines()` — clears and rebuilds spec lines from `product_template_attribute_value_ids`, sorted by PTAV id.
- `create()`/`write()`/`read()` — force recompute of spec lines on create, on relevant field writes, and whenever `read()` is called for that field (belt-and-suspenders freshness; see [[09_known_issues]] for perf note).
See also: [[02_data_flow#Flow 4]]

## ResCompany / ResConfigSettings — inherit
File: `models/res_config_settings.py`
Status: [ACTIVE]
Purpose: Company-level toggle and formatting knobs for internal reference generation, exposed in Settings.
Key Fields (on `res.company`, related onto `res.config.settings`):
- `sh_product_int_ref_gen` (Boolean) — master feature toggle
- `sh_pdt_attr_digit` (Integer) — max characters of each attribute value name to include
- `sh_pdt_seq_sep` (Char) — separator used by `_custom_default_code()` (existing/legacy path)
- `sh_pdt_new_seq_sep` (Char) — separator used by the newer `create()`/`write()` generation path
Critical Methods: `generate_int_ref()` — bulk-regenerates `default_code` for every `product.product` by calling `_custom_default_code()` on each (no batching — see [[09_known_issues]]).
See also: [[02_data_flow#Flow 3]]
