# Architecture / mavjud kod va rejalashtirilgan arxitektura

**Status:** 2026-11-19 holatiga MVP kodni o‘qish asosida. Tizim hali production uchun tayyor emas.

## Texnologiya va kirish nuqtalari

| Qatlam | Real fayl | Izoh |
|---|---|---|
| App/start | `app/main.py`, `app/db.py` | FastAPI router, DB dependency, sessiya |
| Auth/RBAC | `app/security.py`, `app/ui.py`, `app/controllers/auth.py` | Parol hash, imzolangan cookie/session, CSRF, rol |
| Tuman | `app/controllers/district.py` | maktab, maktab admin, o‘quv yili, fan katalogi, audit |
| Maktab | `app/controllers/school.py` | xodim, sinf, setka, dars yuklamasi, soat so‘rovi |
| O‘qituvchi | `app/controllers/teacher.py` | shaxsiy soat, soat o‘tkazish/almashtirish, rozilik |
| Ustama | `app/controllers/bonus.py` | 823 davr, baholash, majlis, tasdiq |
| Qoidalar | `app/services.py` | 3271/823 prototip; hisoblar hardcoded |
| View | `app/templates/*`, `app/static/*` | server-rendered Jinja + Bootstrap |
| DB | `app/models.py` | SQLAlchemy, migratsiyasiz schema |
| Test | `tests/test_rules.py`, `test_http.py`, `test_bonus_http.py` | unit va `TestClient` HTTP regression |

## ORM inventari (haqiqatan kodda mavjud)

- Tashkiliy: `District`, `School`, `User`.
- Normativ/katalog: `AcademicYear`, `Subject`, `PolicyVersion`.
- Kadrlar: `Employee`, `EmployeeSubject`.
- O‘quv rejasi: `ClassGroup`, `CurriculumLine`.
- Yuklama/qaror: `CouncilDecision`, `Allocation`, `HourChangeRequest`.
- Ustama: `BonusPeriod`, `BonusAssessment`, `BonusCriterion`, `BonusCriterionScore`, `BonusMeeting`.
- Qo‘llab-quvvatlash: `AuditLog`, `Notification`.

## Kontekst izolyatsiyasi va bog‘lanishlar

`District → School → Employee → EmployeeSubject → Subject`

`School + AcademicYear → ClassGroup → CurriculumLine → Allocation → Employee`

`School + AcademicYear → CouncilDecision → Allocation / HourChangeRequest`

`School + AcademicYear → BonusPeriod → BonusAssessment / BonusMeeting`; `BonusAssessment → BonusCriterionScore → BonusCriterion`.

**Bir maktabning User.id / Employee.id / ClassGroup.id ni boshqa maktab so‘roviga qo‘yish hech qachon ma'lumotga kirish bermasligi kerak.** Ayniqsa `BonusAssessment` maktabi `BonusPeriod.school_id` orqali aniqlanadi; tugmalar va Jinja filtr yetarli emas.

## Tavsiya qilingan modul chegaralari (refaktor uchun)

Yangi qoidalar ko‘payganda `app/services.py` ni birdan o‘chirmasdan, test bilan bosqichma-bosqich quyidagilarga ajrating:

```text
app/
  domain/
    policies/             # effective-date legal policy snapshots
    curriculum/           # calendar, grade, subject, language and subgroup rules
    allocations/          # priority, fairness, annual workload, consent
    bonus/                # criteria, funds, votes, award types
  repositories/           # school/year scoped queries
  services/               # workflow/use-case transactions
  controllers/            # HTTP only, no direct complex legal math
  templates/             # Uzbek UI, district/school/teacher
  migrations/            # Alembic revision files (future)
```

Bu **taklif**: hozir bu papkalar yo‘q. Agent ularni yaratsa, oldin kerakli `app/services.py` funksiyalarini mavjud testlar bilan qayta yo‘naltirsin.

## Muhim model kamchiliklari / migratsiya zarurati

1. `AcademicYear.active` bir nechta qatorga `True` berishga hozir DB constraint yo‘q; unifikatsiya va per-district/per-school yil siyosati belgilanmagan.
2. `School.code` global unique: kelajakda tumanlararo kod takrorlansa `(district_id, code)` kabi composite uniqueness talabi chiqishi mumkin.
3. `CurriculumLine.weekly_hours`, `Allocation.weekly_hours`, `BonusAssessment.score`, `rate`: hozir `Float`; yaxlitlik/0.5 qadam uchun server hamda DB constraint, pul uchun `Numeric` va `Decimal` zarur.
4. `Employee` bir vaqtning o‘zida bir maktabga bog‘langan; xodimning mehnat shartnomasi, qisman bandligi, o‘rindoshlik va tarixiy transfer uchun alohida `Employment` kerak.
5. `Employee` da toifa/sertifikatlar `bool` maydonlar; `TeacherCredential` va fayl+haqiqiylik tasdiqlash, vaqt/daraja/fan bog‘lanishi kerak.
6. `ClassGroup` da shahar/qishloq, filial, maxsus sinf, inklyuziv va rasmiy istisno/kelishuv uchun tasdiqli `ClassFormation` kerak.
7. `CurriculumLine` faqat bir fan-sinf satri uchun `groups` integer; guruhlarga bo‘linish individual guruh, til, o‘quvchilar taqsimoti va istisnolar bilan modellashtirilishi kerak.
8. `Allocation.state`: `draft`, `approved`, `superseded`; tarixiy snapshot, `valid_from/to`, o‘quv yili, approved_by/at, version + immutable ledger zarur.
9. `BonusMeeting` yig‘indi sonlarni saqlaydi; haqiqiy a'zolik/ishtirok/vote/COI/elektron imzo uchun yangi jadvallar kerak.
10. `PolicyVersion` bor, ammo hisoblash servislariga to‘liq ulanmagan. Sxema uchun `policy_version_id` har tasdiqlangan qarorda saqlansin.
11. `AuditLog` oddiy text; o‘chirilmas append-only log, old/new snapshot, correlation_id va IP/device muvofiq maxfiylik siyosati kerak.
12. **Alembic yo‘q**; ishlab chiqarish DB ga `Base.metadata.create_all` bilan versiyaviy o‘zgarish kiritish taqiqlansin.

## Atomiklik / izchillik

Har bir o‘zgartirish `BEGIN → scoped lock → validate → persist history + new state → audit → COMMIT` shaklida. Soat almashganda *manba va qabul qiluvchi yuklamasi* bitta tranzaksiyada yangilansin; `SELECT ... FOR UPDATE` PostgreSQL uchun rejalashtirilsin. Dublikat `request` yoki parallel approvelarda idempotency key va `version` (optimistic locking) ishlatilsin. Response muvaffaqiyatdan oldin yozuvlar DB ga commit bo‘lsin.

## Maʼlumotlar tipi / UI tili

- Ekranlar: o‘zbek lotin, `Oʻ`, `Gʻ`, `sh`, `ch` bo‘yicha imloni tekshirish; boshqa til kerak bo‘lsa tarjima qatlamidan foydalanish.
- Texnik identifikatorlar va DB maydonlar inglizcha `snake_case`; API contract JSON bo‘lsa `pydantic` schema.
- Sana: `YYYY-MM-DD`, TZ `Asia/Tashkent` ko‘rsatishda; DB UTC offset-aware migratsiya rejasini ko‘rib chiqing.
- Pul: `Decimal` yoki `NUMERIC`, `uzs` valyuta va rounding policy aniq hujjat bilan.

## Non-goals

Bu loyiha **eMaktab**, **UzASBO** yoki **ERP** ning rasmiy o‘rnini egallamaydi va ularning norasmiy API/DBlariga kirishga ruxsat bermaydi. Avtomatik qaror va rasmiy imzo huquqi bor degan taxmin bilan kod yozmang.
