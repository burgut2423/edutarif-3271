# AI handoff / boshqa agentga loyiha topshirish

**Last verified:** 2026-11-19 (repo file inventory and tests inspected). **Status:** GitHub private repository `burgut2423/edutarif-3271`, branch `main`. Ushbu handoff vazifa tugagach yangilanadi.

## Agent uchun 60 soniyalik xulosa

- **Nima:** 3271 dars taqsimoti + 823 ustama uchun tuman, maktab, o‘qituvchi, ishchi guruh web MVP.
- **Nimasi bor:** `app/main.py`, 5 controller (auth, district, school, teacher, bonus), `app/models.py` dagi 19 model, `app/services.py` hisoblash prototipi, Jinja/Bootstrap sahifalari, CSV eksport, dastlabki testlar.
- **Nimasi yo‘q:** Alembic, to‘liq 133-son fan-by-grade reja importi, normativga mos yillik 2322 hisob, haqiqiy 823 kriteriy/evidence/working group, rasmiy ERP/UzASBO API, production security hardening.
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
4. PostgreSQL production target, SQLite tests. Migration must be introduced before real deployment.
5. GitHub Private repository. Never commit `.env`, real PII, passwords, signing keys, DB.

## Navbatdagi ishlar (aniq tartib)

- **NEXT 1 — P0-01:** Alembic schema migration o‘rnatish, DB revision run; tests.
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

- **2026-11-19 — AI agent hujjatlari qo‘shildi:** `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules/edutarif.mdc`, `.claude/skills/edutarif-development/SKILL.md`, `.github/copilot-instructions.md`, `skills/edutarif-development/SKILL.md`, `references/` va `docs/AI_HANDOFF.md`. Kodning mavjud ish mantiqi o‘zgartirilmagan.

### Done / Tests

- `47` ta dastlabki loyiha fayli GitHubga oldin yuklangan; yangi skill fayllari ushbu handoff commitida qo‘shiladi.
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
