# EduTarif AI Agent Backlog — tartiblangan ishlar

Bu *master task list*. Agent vazifani tanlaganda `TASK ID`, dependency, acceptance criteria, test va xavfni PRda qayd qiladi. Bitta agent bir vaqtning o‘zida kerakmas ko‘p modulni rewrite qilmasin. Ustuvorlik: **P0 — xavfsizlik/normativ haqqoniylik**, P1 — to‘liq workflow, P2 — qulaylik va integratsiyalar.

## P0 — productiondan oldingi bloklovchi vazifalar

### P0-01 — Alembic va DB sxema migratsiyalari

**Dependency:** yo‘q. **Done when:** mavjud SQLAlchemy modellardan Alembic initial migration, SQLite dev + PostgreSQL testida upgrade/downgrade sinovi; `init_db` faqat development uchun; kelajak sxema o‘zgarishi maʼlumot yo‘qotmasdan. `README` yangilangan. **Risk:** real DBga qo‘llashdan oldin backup va operator tekshiruvi.

### P0-02 — Tenant/RBAC xavfsizligini to‘liq taftish

**Dependency:** yo‘q. **Done when:** `app/controllers/*` route jadvali tuzilgan; har bir read/write/CSV `school_id` scope, teacher ownership, 823 permissions, login/cookie/CSRF; A school → B school IDOR testlar; inactive user/school tests. Xato handling 403/404 no-PII. **Risk:** ruxsatdan tashqari xodim maʼlumotlari chiqishi.

### P0-03 — 3271 15/16/17-bandlarni sana bilan versiyalash

**Dependency:** P0-01. **Done when:** `PolicyVersion` real hisobga ulanadi; 2025/26 va 2026/27 uchun `effective_from`/source metadata, hujjat tafsilotlari, `TeacherCredential`, fanga mos tan olingan sertifikat, amal qilishi, qayta tayyorlash, `review_required` holati; 3271-1 ustuvorlik qoidalari testlari. **Risk:** xato toifa/sertifikat ustuvorligi.

### P0-04 — 2026/27 fan × sinf × til tayanch o‘quv reja

**Dependency:** P0-01, P0-03. **Done when:** vazirlikning 133-son buyrug‘iga mos *tekshirilgan* fan-by-grade matritsa, turli taʼlim tillari/variantlar, source/ilova/version; import & dry-run, per-class gap analysis, sinf/fan jami soat validation, veb preview. Noma'lum farqlar manual review bo‘lsin. **Risk:** setkani umumiy soat bilan noto‘g‘ri hosil qilish.

### P0-05 — Guruhlarga bo‘lish va sinflarni rasmiy komplektlash

**Dependency:** P0-04. **Done when:** rasmiy guruhga bo‘linish shartlari source clause bilan, o‘quvchi soni/taʼlim tili/istisno, approved evidence, guruhlar soni faqat validatsiyadan keyin; 1–4, 5–11, chekka holatlar testlari. **Risk:** fan yuklamasini ikki baravar noto‘g‘ri hisoblash.

### P0-06 — To‘liq yillik mehnat yuklamasi va adolatli engine

**Dependency:** P0-03, P0-04, P0-05. **Done when:** 18/18 va 20/16 segmentlar, aralash pedagog, kalendar, yillik 1.5 stavka/2322 soat huquqiy validatsiyasi, mavjud yuklama va teng ustuvorlik explainable preview, manbasi/istisno/manual override/rozilik. `used_rate` ilgari MVP ekanligi saqlangan. Test: aralash 4/5-sinf, 1.5 limit, double allocation, epoch version. **Risk:** noto‘g‘ri tarifikatsiya.

### P0-07 — 823 mezonlar/ishchi guruh/qaror to‘liq moduli

**Dependency:** P0-01, P0-02. **Done when:** amaldagi 823 ilovalarining criterion-by-criterion bahosi va dalillari, real guruh aʼzolari/vakilligi, COI, quorum, votes, bayonnoma, foiz va fond limit, kvartal/muddat, direktor buyrug‘i, versioned approvals, double-grant concurrency tests. 50% qoidasining tatbiq doirasi tekshirilgan. **Risk:** noto‘g‘ri moliyaviy qaror.

### P0-08 — Xavfsiz production hardening

**Dependency:** P0-02, P0-01. **Done when:** login rate limit, session expiry/revoke, 2FA (mas'uliyatli rollarda), backups/restore drills, security headers, secret handling, dependency scan, upload safety, PostgreSQL locking, logs/alerts va operator deployment checklist. **Risk:** credential/theft/data loss.

## P1 — to‘liq foydalanuvchi jarayonlari

### P1-01 — Kadrlar moduli

`Employment`, xodim shartnomasi, ishga olish/bo‘shash, o‘rindoshlik, toifa, sertifikat daraja, hujjat tekshiruvi, tarix va xodimga hisob biriktirish. **Acceptance:** sana/tashkilot/fan bo‘yicha moslik, privacy va audit.

### P1-02 — Soat o‘tkazish/almashtirishni to‘liq davlatga moslashtirish

Request state machine, yozma rozilik, kengash qarori, to‘liq/yarim soat, B o‘qituvchining yangi fan huquqi, atomiklik, revoke/history, o‘qituvchiga xabarnoma. **Acceptance:** double spend impossible, history intact, IDOR test, rejections explained.

### P1-03 — Rasmiy tarifikatsiya va tasdiqlash

Maktab/kengash/tuman/vakolatli moliya rollari huquqiy tahlil; imzo/dalil, hisobot versiyasi, Excel/PDF shakli, tasdiq statusi va changelog. **Acceptance:** tasdiq huquqi qonunga mos role; approved only through documented action.

### P1-04 — Maktab + tuman dashboard

Maktab/kadr/sinf/soat/ustama aggregate, remaining/overloaded, filter/export; maxfiy baho yoki 823 qarori noto‘g‘ri rolga ko‘rinmasin. **Acceptance:** 50+ maktab / minglab xodim, server-side pagination and indexes.

### P1-05 — Apellyatsiya va notifications

O‘qituvchi ustuvorlik/soat/baho natijasiga hujjatli murojaat, tegishli qaror organi, deadline (faqat huquqiy manba), notification. **Acceptance:** status + SLA policy, no self approval, trail.

### P1-06 — Maxsus 823 turlari

Direktor va o‘rinbosar KPI, sport, metodbirlashma, mentor, musiqa/cholg‘u, mukofot va moddiy yordam, Zakovat; har biri alohida normativ version/award type. **Acceptance:** oqimlar o‘zaro aralashmaydi; fond limiti bilan.

## P2 — integratsiya, ergonomika, avtomatlashtirish

### P2-01 — Rasmiy ERP / UzASBO integratsiyasi

Ruxsatlar, API, sandbox, mapping, rasmiy read/write contract tasdiqlangach. **Acceptance:** import dry-run, idempotency, audit, retry/error, least privilege. Ruxsatsiz scraping yo‘q.

### P2-02 — Import/Export Center

.xlsx/.csv, rasmiy tarifikatsiya va kadrlar importi, dedup, row errors, previews, PDF dalil. **Acceptance:** shaxsiy maʼlumotlar himoyalangan; Excel formula injection yo‘q.

### P2-03 — UI/UX Premium AdminLTE-like

Responsive role dashboards, icons, empty state, Uzbek lotin imlo, tabular filters, search, teacher timeline, mobile accessibility. **Acceptance:** desktop/tablet/phone; ekran accessibility/safe actions.

### P2-04 — Performance/monitoring

PostgreSQL DB indexes, pagination, async/background jobs (server workers), queue, health checks, metrics, backup, Sentry-like alerts. **Acceptance:** 50–100+ maktab sintetik load test, P95 API goal hujjatlashtirilgan.

### P2-05 — Public deployment / operator runbook

Vercelga mos ishlab chiqarish **faqat** mos DB/ASGI/long-running jobs talablariga ko‘ra, aks holda boshqa Python hosting; HTTPS, DB migration, CI/CD, rollbacks, license. **Acceptance:** demo synthetic data, production secrets private, smoke tests, runbook.

## Agent sifatini baholash

Har task uchun PRda quyidagini tekshiring:

- [ ] ID + dependency + source rule / UI requirement yozilgan.
- [ ] DB migration/revision va rollback kerakligi baholangan.
- [ ] Maktab/yil/ruxsat, xodim/rol, privacy va CSRF testlangan.
- [ ] Business rule unit + HTTP regression test qo‘shilgan.
- [ ] Human decision hech qachon avtomatik imzoga aylantirilmagan.
- [ ] `docs/AI_HANDOFF.md` yangilangan.
- [ ] Qolgan bloklovchilar aniq yozilgan.
