# Barcha rollar, ekranda ishlash va holatlar

## Asosiy ekranlar va mavjud endpointlar

| Rol | MVP endpoint/view | Mavjud vazifa | Takomillashtirish |
|---|---|---|---|
| Har kim | `/login`, `/logout`, `/change-password` | autentifikatsiya | rate limit, 2FA, recovery |
| Tuman admin | `/schools`, `/settings`, `/audit` | maktab, admin, yil, fan, audit | dashboard, role policy, filiallarga moslik |
| Maktab admin | `/school/staff` | kadr/fan | mehnat shartnomasi, diplom verifikatsiyasi |
| Maktab admin | `/school/classes` | sinf | rasmiy komplektlash, filtr, tasdiq |
| Maktab admin | `/school/grid` | fan/soat/guruh | 133-son shablon, validatsiya |
| Maktab admin | `/school/allocations` | yuklama, preview, tasdiq, CSV | yillik hisob, snapshot, Excel/PDF |
| Maktab admin | `/school/requests` | arizaga qaror | atomiklik, idempotent, versiyalar |
| O‘qituvchi | `/me` | yuklama/ustama/so‘rov/rozilik | notification, history, appeal |
| Maktab/ishchi guruh | `/bonus` | davr, baholash, majlis, grant | mezon-dalil, real aʼzolar, mablag‘ ledger |

URL prefikslari `app/controllers/` dagi routerlardan keladi; agent aniq endpointlarni koddan tasdiqlasin.

## End-to-end: tuman → maktab → xodim → dars

1. `district_admin` maktab kodini/nomini kiritadi, tashkilot tumanga ulanadi.
2. Tuman admin `school_admin` uchun alohida login va vaqtinchalik parol yaratadi.
3. Tuman admin yil (`AcademicYear`) va fan (`Subject`) katalogini yaratadi.
4. Maktab admin xodimni `Employee`, login/role (ixtiyoriy), fanini `EmployeeSubject` bilan kiritadi.
5. Sinf `ClassGroup(grade, section, student_count, language, academic_year)` yaratiladi. Komplektlash hujjati tasdiqlanadi.
6. O‘quv reja maʼlumotiga mos `CurriculumLine(subject, weekly_hours, groups, source_ref)` kiritiladi, tekshiruvdan o‘tadi.
7. `distribution_preview` taklif qaytaradi; normativ ustuvorlik, malaka, yillik stavka, soatlar sarfi va adolatlilik tekshiriladi.
8. Pedagogik kengash `CouncilDecision` hujjatini yaratadi.
9. `Allocation` kengash qaroriga ulanib tasdiqlanadi. O‘qituvchi kabineti tasdiqlangan satrlarni ko‘radi.
10. CSV orqali vaqtinchalik eksport; rasmiy ruxsat bilan ERP/UzASBO integratsiyasi keyinchalik.

## O‘qituvchi soat o‘tkazish so‘rovi

**Taklif etilgan to‘liq state machine:**

`draft → submitted → recipient_review → recipient_accepted → school_review → council_approved → applied`

Yon holatlar: `recipient_rejected`, `school_rejected`, `withdrawn`, `expired`, `requires_revision`, `failed_validation`.

MVP da `HourChangeRequest.status` `pending/approved/rejected`, `recipient_consented: bool`. Yangi statuslar va migratsiya kiritmasdan UI da mavjud deb ko‘rsatmang.

**Jarayon:**

- `teacher` o‘zining tasdiqlangan allocation ID sini, oluvchi xodimni, `transfer` yoki `swap`, soatni, sababni tanlaydi.
- So‘rov 0.5 qadamda, mavjud real soatdan oshmasligi, maktab/yil/fan/sinf malakasi mosligi tekshiriladi.
- `swap` oluvchining tasdiqlangan allocationini ham ko‘rsatadi; ikki satr bir maktab, bir o‘quv yili va almashtirishga qonunan mos bo‘lsin.
- Qabul qiluvchi **shaxsiy hisobidan** rozilik yoki rad javobini beradi; uning o‘rniga admin rozilik bermaydi.
- Maktab admin ariza va kengash qarorini ko‘radi; yakunda ikki xodimning holati, amal qilish davri va yuklamani atomik tekshiradi.
- Barcha qarorlar audit va notification bilan. Avvalgi allocation snapshot saqlanadi; ID yoki hajm yo‘qolmaydi.

### `transfer` va `swap` ning farqi

- `transfer`: A fan/sinf yuklamasining `x` soati A dan B ga o‘tadi. A->B uchun B da o‘qitish huquqi, 1.5 limit va setka sarfi tekshiriladi.
- `swap`: A ning `x` soati B ning `y` soati bilan almashadi. Har bir pedagog yangi fan/sinfga malakali bo‘lishi, haftalik/yillik meʼyor saqlanishi kerak. `x/y` siyosati huquqiy tekshiruvdan keyin aniqlansin, hozir `weekly_hours` bitta miqdor.
- So‘rovni **o‘zi avtomatik qo‘llash** xato; tasdiqlovchi hujjat talab qilinadi.

## Ustama workflow

`period_created → criteria_entered → evidence_reviewed → workgroup_meeting → quorum/vote_checked → approved → director_order_recorded → export_ready → period_closed`

MVP ning haqiqiy holati: `BonusAssessment.state` `draft/approved`, `BonusPeriod.status` asosan `draft`; ballda dalil bo‘lsa ham mezon uchun to‘liq workflow yo‘q. Yangi event/state ni mavjud deb ko‘rsatmaslik.

## Hisobotlar

- Tuman paneli: maktablar soni, sinflar, fanlar, dars yuklamasi umumlashtirilgan (maxfiy ustama qaroriga aralashmasin).
- Maktab: grade/section, subject, teacher, week, full-rate equivalent, remaining/overbooked, approval, audit.
- O‘qituvchi: o‘z yili bo‘yicha fan-sinf-soat, 1–4/5–11 segment, so‘rovlar va ruxsat etilgan ustama maʼlumotlari.
- 823: ishchi guruh uchun davr, dalillar, ball, fond, to‘lovlar; tegishli maxfiylik va rol.
- Exportlar current filter+school_id+year+policy_version bilan; har eksport tarixi ham auditlansin.

## UX minimal talablari

- Sidebar tuman/maktab/o‘qituvchi roliga qarab farqlansin; faqat tugmani yashirish authorization emas.
- Mobile-first responsive, jadvalda filter/sort/pagination; katta dataset uchun server-side pagination.
- Formalarda inline validation, sanalar, qonuniy dalil `source_ref` va tasdiqlovchi organ ko‘rsatilgan bo‘lsin.
- `review_required`, `unverified`, `draft`, `approved` aniq farqlansin; noaniq tavsiya `approved` ko‘rinmasin.
