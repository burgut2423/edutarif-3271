# GitHub Copilot repository instructions

Follow **`AGENTS.md`** as the primary repository-wide policy. Read `docs/AI_HANDOFF.md`, `skills/edutarif-development/SKILL.md`, and task-specific references under `skills/edutarif-development/references/`.

Do not merge 3271 allocation and 823 bonus logic. Preserve `school_id` scoping, separate 1–4 and 5–11 rules, audit, CSRF, approvals, and effective-dated legal policies. Do not commit secrets or real staff data. Test each change with `python -m pytest -q`, add missing tests, and update the handoff document. This code is a provisional MVP, not a certified payroll or tariff engine.
