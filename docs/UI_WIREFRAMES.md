# UI interface concepts (responsive AdminLTE-like)

> Sample composite: [3 dashboard concepts](mockups/ui_overview.jpg). Visual prototypes, **not finished dynamic screens**. All names, KPI counts, rates, and percentage labels in previews are illustrative and NOT reliable compliance or bonus determinations.

## District administrator

Sidebar: dashboard, schools, employees (aggregate, permission-checked), 3271, 823 aggregate, curriculum periods, audit, settings.
Header: active year, search, notifications, account, organization.
Content: cards for `schools`, `employees`, `class_groups`, weekly hours (aggregate).
Main table: schools; code, title, language, classes, staff, hours, unverified plans, actions; server-side filters and pagination. Never display cross-school employee personal documents without explicit authorized purpose.

## School administrator

Sidebar: employees, qualifications, classes, weekly subject grid, hour allocation, requests, bonuses (823), audit.
Content: weekly hour matrix from **approved** official grade x subject x language source; current allocation, under/over assignment, 1–4 vs 5–11 explained rules, source link and verification status; 823 period limit and committee review. An automated recommendation must be labeled **TAVSIYA** and needs authorized council decision.

## Teacher portal

Self-only identity; approved lessons by class/subject/weekly hours; request to transfer/swap with consent; state timeline; own review/appeal; 823 own amount only when approval published. Show weekly hours and workload estimates with clear provisional labels. Never allow teacher to directly mutate another employee's allocation.

## Visual tokens

- Sidebar: dark navy, active menu turquoise; canvas: cool off-white; cards: white, subtle shadow.
- Typography: Inter-like sans-serif, legible Uzbek Latin / apostrophes; clear numerals and dates.
- Desktop 1440px: 240px sidebar + 12-column grid; tablet collapses sidebar; mobile cards stack, tables horizontally scroll and actions remain accessible.
- Semantic colors: green = confirmed, amber = needs attention, red = invalid, blue = informational, purple = 823 module. Avoid color alone for meaning.
- WCAG: keyboard focus, accessible labels, min 44px targets, responsive dialog, CSRF protected forms, role-based actions.

## Next implementation (P2-03)

Design mockups do not automatically change `app/templates/*`. Implement each screen incrementally with HTTP tests, tenant filters, and real database computed stats; avoid hardcoding fake approval percentages or monetary data into live dashboards.
