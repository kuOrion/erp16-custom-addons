# Controllers
Status: [ACTIVE] — N/A for this module
Back to [[00_overview]]

This module has no HTTP controllers — there is no `controllers/` directory and nothing registers an
`http.route`. All entry points are Odoo model methods invoked from view buttons/onchanges
([[04_views_xml]], [[03_models]]) or from scheduled `ir.cron` jobs ([[07_csv_data]]). Still true after
v16.0.6 — the new release/reuse/history feature is implemented entirely as model methods and view
button actions, no controller added.
