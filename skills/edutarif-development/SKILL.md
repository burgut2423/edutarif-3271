---
name: edutarif-development
description: Continue building, reviewing or testing the EduTarif 3271/823 Uzbek school workload allocation and director-fund bonus application. Use for tasks involving districts, schools, employees, classes, curricula, teacher load, 3271 priority, hour transfer/swap requests, 823 assessments, role permissions, migrations, UI or integrations.
---

# EduTarif Development Skill (AI agentlar uchun to‘liq ish protokoli)

## Qachon ishlatiladi

Ushbu skill `burgut2423/edutarif-3271` repositorysida **yangi funksiya**, xatolikni tuzatish, normativni yangilash, maʼlumotlar bazasini kengaytirish, testlash, mobil/desktop UI yoki deploy haqida topshiriq bo‘lsa ishlatiladi. Ushbu skill boshqalardan mustaqil o‘qiladigan loyiha qo‘llanmasi, lekin `AGENTS.md` qoidalari undan ustun.

## Tezkor ishlash algoritmi

1. `AGENTS.md`, `docs/AI_HANDOFF.md`, `README.md` va kerakli reference faylni **to‘liq** o‘qing.
2. `git status --short && git log -5 --oneline`, `python -m pytest -q` bajaring.
3. Bitta aniq natija tanlang. Talabni **actor → trigger → validation → state change → audit → notification → rollback/error** formatida yozing.
4. Ish boshlashdan oldin **normativ** talabmi yoki **mahsulot** talabi ekanligini ajrating. Normativ bo‘lsa rasmiy hujjat va amal qilish sanasini toping; noaniqlik bo‘lsa `manual_review_required` va inson tekshiruvini belgilang.
5. `models → migration → services → controller → Jinja view → tests → docs` zanjirini ko‘rib chiqing. Hammasi har safar o‘zgarishi shart emas; lekin har biri bo‘yicha qaror yozing.
6. Har bir ID uchun `school_id` maktab doirasi, rol, CSRF, izchil tranzaksiya va auditni tekshiring. UI uchun server tarafidagi tekshiruvni chetlab o‘tish mumkin emas.
7. Testlar o‘tsin; xavfli regressiyalarni tekshiring. Natijani `docs/AI_HANDOFF.md` da qayd eting.
8. Foydalanuvchiga commit/PR, aynan nima ishlashi, testlar va nima qolganini aniq ayting. Asossiz "mukammal" yoki "qonuniy 100%" deyish mumkin emas.

## Koddan boshlang, taxminlardan emas

- **Backend:** FastAPI `app/main.py`; controllerlar `app/controllers/`.
- **ORM:** `app/models.py`; hozir Alembic migratsiya yo‘q.
- **Biznes:** `app/services.py`: `priority_rank`, `qualified`, `used_rate`, `validate_allocation`, `distribution_preview`, `bonus_rate`, `bonus_cap_ok`, `bonus_fund_ok`, `audit`.
- **UI:** `app/templates/*.html`, `app/static/*`; Bootstrap 5.3 — AdminLTE uslubidagi hozirgi dizayn.
- **Testlar:** `tests/test_rules.py`, `tests/test_http.py`, `tests/test_bonus_http.py` va fixture `tests/conftest.py`.
- **Ishlatish:** Python 3.12, `pip install -r requirements.txt`, `.env` (`.env.example` dan; secretni almashtrish), `python -m scripts.bootstrap_admin`, `uvicorn app.main:app --reload`; `pytest -q`.

## Asosiy biznes obyektlari va ruxsatlar

- `district_admin`: `District`, `School`, umumiy `AcademicYear`, `Subject`, maktab adminlari, audit; 823 qarorini tasdiqlamaydi.
- `school_admin`: o‘z `School` uchun `Employee`, `EmployeeSubject`, `ClassGroup`, `CurriculumLine`, `Allocation`, `CouncilDecision`, `HourChangeRequest`; 823 baho/davrni tayyorlash.
- `teacher`: `User.employee_id` bo‘yicha o‘z tasdiqlangan yuklamasi, 823 bo‘yicha o‘z natijasi, soat o‘tkazish/almashtirish uchun **ariza**; tasdiqlash vakolati yo‘q.
- `bonus_committee`: faqat o‘z maktabining ustamasi, haqiqiy bayonnoma/rol asosida; manfaatlar to‘qnashuvi tekshiriladi.

**To‘liq model inventari va taxminiy workflow:** `references/ARCHITECTURE.md` hamda `references/WORKFLOWS.md`.

## 3271 moduli: agent uchun cheklovlar

- 1–4 va 5–11 sinf meʼyorlarini farqlang; `grade<=4` orqali har qanday maxsus holatni soddalashtirib yubormang.
- Ustuvorlik bir nechta hujjatdan tanlansa, amal qilish muddati va fanga **mosligi** tekshirilsin; sertifikat shunchaki `bool` bo‘lishi yetarli emas.
- Dars soati setkasi **o‘quv rejasi versiyasi, ta’lim tili, sinf, o‘quv yili va guruhga bo‘linish** asosida hosil bo‘lsin. O‘qituvchi soati = jadvaldagi fan o‘quv soati × tasdiqlangan guruhlar (istisnolar alohida).
- `distribution_preview` — tavsiya, rasmiy qaror emas. Teng ustuvorlik va yozma roziliklar izlanadigan asos bo‘lishi kerak.
- `used_rate`/`annual_workload_estimate` taxminiy; to‘liq 2322 soatlik kalendar tekshiruvi mavjud emas. Uni *production-valid* deb chiqarmang.
- `transfer`/`swap` uchun rozilik, tegishli pedagogik kengash qarori va bitta tranzaksiya kerak; avvalgi yozuvlarni o‘chirib yubormang.
- **Batafsil:** `references/RULES_3271.md`.

## 823 moduli: agent uchun cheklovlar

- Ustama dars taqsimotidan mustaqil baholanadi; direktor jamg‘armasi meʼyorlarini ustunlik sifatida 3271 algoritmiga aralashtirmang.
- Ustama uchun faoliyati asosida baholash **har bir mezon + dalil**; inson tasdig‘i, ishchi guruh, kvorum, ovoz, bayonnoma, buyruq, limit va 50% qoidasining tegishli qo‘llanishi tekshiriladi.
- `bonus_rate` dastlabki kalkulyator; maxsus bonuslar/yangi qarorlar yangi versiyali sxemaga ko‘chishi shart.
- `bonus_committee` hisobini yaratish ishchi guruhning haqiqiy tarkibi va vakolatini tasdiqlamaydi.
- **Batafsil:** `references/RULES_823.md`.

## Har bir kichik ish uchun generatsiya cheklovi

- Qo‘shimcha model: SQLAlchemy FK/unique/check, maktab va yil identifikatori, status, vaqt/audit, migratsiya, test.
- Qo‘shimcha endpoint: server-side `role + tenant + input validation + CSRF`, keyin servis chaqirish.
- Qo‘shimcha UI: o‘zbekcha tushunarli sarlavha, xatolik, bo‘sh holat, qayta tasdiqlash, mobil moslashuv, klaviaturada ishlashi.
- Hisoblash: sof funksiya bo‘lsin; pul uchun `Decimal`, vaqt/versiyalar uchun haqiqiy sana.
- Tashqi servis: faqat ruxsatli API, hujjatlashtirilgan data mapping, retry/idemponent, ajratilgan secret, monitoring.
- Huquqiy noaniqlik: ochiq `manual_review` / `not_supported` status, soxta avtomatik hisob yo‘q.

## Qanday navbat bilan davom etiladi

Avval `references/BACKLOG.md` dagi **P0** vazifalar, so‘ng P1, keyin P2. Kod sifatini va maʼlumot xavfsizligini buzmasdan bir-biriga bog‘liq ishlarni ajrating. Har bir vazifa uchun `references/TEST_PLAN.md` dan testlar, `references/SECURITY.md` dan xavfsizlik tekshiruvlari, `references/INTEGRATIONS.md` dan import/eksport talablarini qo‘llang.

## Keyingi agentga topshirish (`docs/AI_HANDOFF.md`)

Yakunida quyidagini yozing:

- **Commit/PR:** URL/SHA; branch; qaysi task ID.
- **Done:** qaysi endpoint, modul, model, view real ishlaydi.
- **Tests:** buyruq va natija; bajarilmagan testni yashirmang.
- **Legal validation:** manba, sana, tasdiqlangan/tekshirish talab etiladi.
- **Known gaps / risks:** xavfsizlik, migratsiya, hisob.
- **Next:** bittadan uchtagacha aniq ish, qayta ishlab ketish uchun yo‘nalish.

## Reference hujjatlar

- `references/ARCHITECTURE.md`: qatlamlar, model xaritasi, tranzaksiya chegarasi.
- `references/RULES_3271.md`: 3271 qoidalari, 1–4 va 5–11, test-case'lar.
- `references/RULES_823.md`: 823 mezonlari, fond, ishchi guruh, pul.
- `references/WORKFLOWS.md`: use-case, state machine, o‘qituvchi arizalari.
- `references/SECURITY.md`: RBAC, tenant, maxfiylik va deployment xavflari.
- `references/TEST_PLAN.md`: test rejasi va regression matriks.
- `references/BACKLOG.md`: P0/P1/P2 vazifalar va acceptance criteria.
- `references/INTEGRATIONS.md`: ERP, UzASBO, import/eksport, qo‘lda tasdiqlash.

**Hujjat versiyasi:** 2026-11-19. Skill — agent instruksiyasi; huquqiy ekspertiza o‘rniga o‘tmaydi.
