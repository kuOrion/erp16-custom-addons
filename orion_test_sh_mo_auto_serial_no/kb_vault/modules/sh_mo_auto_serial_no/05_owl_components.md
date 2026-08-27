# Frontend JS Components
Status: [ACTIVE] — N/A for this module
Back to [[00_overview]]

This module ships no JavaScript/OWL assets — the `__manifest__.py` `assets` key is absent entirely, and
no `static/` directory exists. All interactivity (button visibility, field requiredness/domains, warning
messages, admin-only tab/button gating) is implemented declaratively via `attrs`/domains/`groups` in
XML views ([[04_views_xml]]) and server-side `@api.onchange` methods in the model layer
([[03_models]]). This remains true after the v16.0.6 release/reuse/history feature — no JS was added.
