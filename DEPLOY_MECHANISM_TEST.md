# Deploy mechanism test marker

This file exists only to give `deploy.sh`'s promote step (`git checkout
<commit>` in `Live_copy_of_Addons`) a real, different commit to move to
while it's being built and tested. Not a module (no `__manifest__.py`),
so Odoo's addons scanner ignores it entirely -- harmless by construction.

Safe to delete once `deploy.sh` is fully built and proven.
