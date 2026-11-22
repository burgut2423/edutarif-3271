# AI handoff / boshqa agentga loyiha topshirish

**Last verified:** 2026-11-19 (P0-01 initial migration, SQLite test, ER schema). **Status:** GitHub private repository `burgut2423/edutarif-3271`, branch `main`. Ushbu handoff vazifa tugagach yangilanadi.

## Agent uchun 60 soniyalik xulosa

- **Nima:** 3271 dars taqsimoti + 823 ustama uchun tuman, maktab, o‘qituvchi, ishchi guruh web MVP.
- **Nimasi bor:** `app/main.py`, 5 controller (auth, district, school, teacher, bonus), `app/models.py` dagi 20 model, `app/services.py` hisoblash prototipi, Jinja/Bootstrap sahifalari, CSV eksport, dastlabki testlar.
- **Nimasi yo‘q:** PostgreSQL migratsiya sinovi, to‘liq 133-son fan-by-grade reja importi, normativga mos yillik 2322 hisob, haqiqiy 823 kriteriy/evidence/working group, rasmiy ERP/UzASBO API, production security hardening.
- **Haqiqiy xavf:** MVP algoritmni yakuniy mehnat haqi yoki normativ qaror deb ishlatish noto‘g‘ri.
- **Birinchi ish:** `AGENTS.md`, `skills/edutarif-development/SKILL.md`, kerakli `references/*.md` fayl; `pytest -q`; `git status`.
- **Backlog:** `skills/edutarif-development/references/BACKLOG.md` (P0-01..P2-05).

## Mavjud funksiyalar haqida ma'lumot

| Modul | Kod joyi | Real MVP holati | Hali zarur |
|---|---|---|---|
| Tuman admin | `district.py` / `schools.html`, `settings.html` | school/create/admin/year/subject/audit | comprehensive role policy, import, approval chain |
| Maktab kadr | `school.py` / `staff.html` | employee CRUD qismi, subject link, teacher login | employment & credentials verification |
| Sinf/setka | `school.py` / `classes.html`, `grid.html` | sinf/year, fan/soat/guruh, approve/verify | rasmiy template and subgroup rules |
| 3271 yuklama | `services.py`, `school.py` | priority preview, 18/20 rate, 1.5 estimate, allocation/approval | full 2322 year, effective policy, explainable decisions |
| O‘qituvchi | `teacher.py`, `teacher.html` | approved hours, transfer/swap request, recipient consent | full state machine, effective dates, permissions audit |
| 823 ustama | `bonus.py`, `bonuses.html` | assessment, basic rate/cap/fund, meeting/approval | criteria-by-criterion, official votes/member identities, revision |
| Audit | `models.py`, `district.py` | simplified activity log | append-only immutable trail, snapshots |
| Testlar | `tests/` | 10 dastlabki test (so‘nggi bajarishda o‘tgan) | P0/P1 edge and concurrency tests |

## Hozirgi jamoa qarorlari

1. Backend Python FastAPI/SQLAlchemy; UI server-side Jinja + Bootstrap (AdminLTE-ga o‘xshash).
2. Tuman admin maktab va umumiy katalogni boshqaradi, maktab admin xodim/setka/soat jarayonini boshqaradi, o‘qituvchi o‘z arizalarini beradi, 823 alohida ishchi guruh vakolatida.
3. Faqat official legal sources, effective dates. No automatic state-certified salary decisions.
4. PostgreSQL production target, SQLite tests. Initial Alembic migration exists; dedicated PostgreSQL validation remains mandatory before production.
5. GitHub Private repository. Never commit `.env`, real PII, passwords, signing keys, DB.

## Navbatdagi ishlar (aniq tartib)

- **NEXT 1 — P0-01:** Alembic initial schema SQLite tekshirildi; faqat izolyatsiyalangan PostgreSQL test va backup/restore drill qolgan.
- **NEXT 2 — P0-02:** barcha route uchun tenant/role/CSRF matrix va regressiya testlari.
- **NEXT 3 — P0-03:** 3271 legal policy + credential+priority proof versioning.

Qolgan ishlar, dependency va acceptance criteria: `skills/edutarif-development/references/BACKLOG.md`.

## Oldin aniqlangan risklar

- `app/services.py` dagi `annual_workload_estimate` yakuniy qonuniy yil hisobini bermaydi.
- `PolicyVersion` mavjud, ammo qoidalar hisobiga to‘liq ulanmagan.
- `BonusMeeting` faqat son/vakil flag, individual ishchi guruh hujjati yo‘q.
- `BonusCriterionScore` modeli bor, lekin to‘liq mezon UI va baholash mavjud emas.
- Guruhga bo‘lish `groups` maydoniga qo‘lda kiritiladi, rasmiy shartlar tekshirilmaydi.
- Migratsiya, rate-limit, 2FA, proper file attachments, PostgreSQL concurrent approval testlari yo‘q.

## Agent ish bitgach shu bo‘limni yangilaydi

### Latest change

- **2026-11-19 — P0-01 initial DB migration (current):**
  `alembic.ini`, `migrations/env.py`, `migrations/versions/20261119_01_baseline_schema_20_tables.py`,
  `scripts/db_migrate.py`, `scripts/schema_report.py`, `tests/test_migrations.py` qo‘shildi.
  `scripts/init_db.py` endi `create_all()` ishlatmaydi (faqat development seed);
  `scripts/bootstrap_admin.py` Alembicga o‘tdi va districtni yaratadi.
  `docs/DB_SCHEMA.md` 20 ta mavjud jadval ER sxemasi, `docs/UI_WIREFRAMES.md` 3 rol ekranlari maketi.
  SQLite clean install, idempotent upgrade, data survive, downgrade, legacy DB refuse testlari o‘tgan.
  **Qoldi:** real PostgreSQL migration smoke test/backup drill, production hardening (P0-02 va P0-08).

- **2026-11-19 — AI agent hujjatlari qo‘shildi:** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/edutarif.mdc`, `.claude/skills/edutarif-development/SKILL.md`, `.github/copilot-instructions.md`, `skills/edutarif-development/SKILL.md`, `references/` va `docs/AI_HANDOFF.md`. Kodning mavjud ish mantiqi o‘zgartirilmagan.

### Done / Tests

- Baseline 20 ta table, 3 ta Alembic migratsiya testi qo‘shildi; keyingi commitda CI testlari tekshiriladi.
- Bu hujjat faqat onboarding; to‘liq yuridik/moliya ekspertizasi o‘tkazilmagan.

### Blockers / questions

- Vazirlik 133-son buyrug‘ining barcha rasmiy ilovalari, maktablar turi va tillari uchun tasdiqli dataset.
- 823 baholash ilovalari va maxsus 2026 o‘zgarishlarining davrga mos yuridik qo‘llash qoidalari.
- Rasmiy ERP/UzASBO API xizmat ko‘rsatish vakolati, contract va sandbox.
- Production hosting, turli taʼlim tashkilotlari soni, privacy/retention siyosati.

## Foydalanuvchi boshqa AI agentiga beradigan prompt

```text
Siz burgut2423/edutarif-3271 private GitHub repositorysidagi EduTarif 3271/823 tizimini rivojlantiruvchi agent siz. Avval AGENTS.md, docs/AI_HANDOFF.md, README.md va skills/edutarif-development/SKILL.md fayllarini to‘liq o‘qing. Keyin references/BACKLOG.md dagi birinchi ochiq P0 taskni tanlang, testlarni ishga tushiring, kerakli kod/model/controller/view/migration/testni yarating. 1–4 va 5–11 meʼyorlarini aralashtirmang; 3271 va 823 vakolatlari alohida. Har bir so‘rovda rol + school_id + year_id + CSRF + audit, moliyada Decimal, huquqiy noaniqlikda manual review. Yangi normativni faqat rasmiy Lex.uz va tegishli vazirlik manbasi, amal qilish sanasi bilan ishlating. Mavjud ishlaydigan kodni buzmasdan, test qo‘shib, GitHub PR/commit tayyorlang. Oxirida docs/AI_HANDOFF.md ni yangilang va real test natijasini, qilingan ishlar va qolgan risklarni yozing.
```

### 2026-11-23 — `darstaqsimot` selektiv integratsiyasi

- Manba: `burgut2423/darstaqsimot`, `main` = `c84983ecff3af0f90e3494050791a266b611d3b6`.
- `POST /school/classes/batch`: 1–11-sinf, 1–10 yangi parallel, takrorlanmaydi, maktab/year scoped, draft + CSRF + audit.
- `GET /school/matrix` va `/school/matrix/export.csv`: maktabga tegishli sinf–fan matritsasi, guruhlar orqali o‘quv soati/pedagogik soat alohida, bo‘sh soat, tasdiqlanish holati, CSV formula injection cheklovi.
- Kod: `app/controllers/matrix.py`, `app/curriculum_matrix.py`, `app/templates/matrix.html`, `tests/test_reused_darstaqsimot.py`.
- Manbadagi avtomatik soat taqsimlash va 823 kalkulyatori tekshiruvsiz ko‘chirilmagan: `docs/DARSTAQSIMOT_REUSE.md`.
- Keyingi agent bu joriy read-only natijani rasmiy fan-soatlar setkasi deb e'lon qilmasin; tasdiqlash va huquqiy mapping alohida.
