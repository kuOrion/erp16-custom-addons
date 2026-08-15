# Pipeline test marker — safe to delete

Deliberate, trivial commit created 2026-08-15 to exercise the real
staging review mechanism end-to-end for the first time on real
production (admin console "Review" button → `git checkout` in
`Staging_copy_of_Addons` → `staging-web` restart → health check).

Not a real module, touches nothing functional. Remove in a follow-up
commit once the review cycle is confirmed working.
