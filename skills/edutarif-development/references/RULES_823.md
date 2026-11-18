# 823 — direktor jamg‘armasi, baholash, qaror, ustama

**Rasmiy manba:** https://lex.uz/uz/docs/-4532496 — VM 30.09.2019 dagi 823-son qarori, uning qo‘shimchalari va tegishli ilovalari. Muhim tahrirlar orasida 2025-10-21 dagi 662-son ham bor. Loyiha `docs/REGULATIONS.md` da 2026-11-11 dagi 617-son hujjatni ham ko‘rsatgan; tegishli hujjatning amaldagi rasmiy matnini **tasdiqlab oling**. Normani sanasiz faqat son bilan saqlamang.

## 3271 dan qat’iy ajratish

3271 dars soati — yuklama; 823 — xodimni rag‘batlantirish. Ustama yoki milliy sertifikat xodimning 3271 ustuvorlik bazasiga faqat tegishli hujjatning mustaqil normasi bo‘lsa taʼsir qiladi. **823 balli 3271 dars soatini oshirmaydi**. Ustama hisobidagi xatolik maosh/soatga avtomatik o‘tmasin.

## Ish jarayonining asosiy obyektlari

`School + AcademicYear -> BonusPeriod -> BonusAssessment -> BonusCriterionScore -> BonusCriterion`

`BonusPeriod -> BonusMeeting + WorkingGroup/Member/Attendance/Vote (future)`

`BonusAssessment -> AwardDecision -> DirectorOrder -> PayrollExport (future)`

MVP jadvallari: `BonusPeriod`, `BonusAssessment`, `BonusCriterion`, `BonusCriterionScore`, `BonusMeeting`, `User` (`bonus_committee`). **Haqiqiy `WorkingGroup`, aʼzolar, individual ovozlar va apellyatsiya modellari yo‘q**. Bularni yaratayotganda audit, sana, tur, vakil tipi va manba dalillar bilan bog‘lang.

## Baholashning asosiy invariantlari

1. `BonusPeriod`: yil/chorak yoki tegishli rasmiy davr, maktab, fond summasi, normativ versiya, holat; pul davrining yopilishi tarixni qulflashi kerak.
2. `BonusCriterion`: rollarga (`teacher`, `psychologist`, `librarian` va alohida turlar) mosligi, max score, dalil turi, amal qilish davri, yuridik band; max ball yig‘indisi tekshiriladi.
3. Har bir mezon bo‘yicha `score <= criterion.max_score`, hujjat/URL/fayl/sertifikat imzosi, baholovchi, ko‘rib chiqish vaqti, rad etish sababi.
4. **Ustama oladigan pedagoglar soni** tegishli norma bo‘yicha umumiy pedagoglarning ko‘pi bilan 50% bo‘lishi: qaysi xodim pedagog sifatida sanaladi, qaysi ustama bu kvotaga kiradi, davrdagi shtat snapshot zarur. `bonus_cap_ok` MVP dastlabki tekshiruv; istisnolar alohida versiyalansin.
5. Fond `fund_limit` maktab/davr uchun tasdiqlangan bo‘lsin; `bonus_fund_ok` hozir tasdiqlangan assessment summasini tekshiradi. Real fonddan maosh fondi, maxsus to‘lovlar va avvalgi majburiyatlar ham alohida nazorat qilinadi.
6. O‘qituvchi va boshqa lavozimlarda foizlar bir xil emas: joriy `bonus_rate` prototipidagi chegaralarni qonunning *amaldagi ilovalari* bilan bandma-band solishtirmasdan yakuniy deb qabul qilmang.
7. Pulda `Decimal`/`Numeric`, rounding policy (masalan, ikki kasr yoki butun UZS) ma'lum bo‘lsin. `amount = tariff_base * rate / 100` formulasi uchun aynan qaysi `tariff_base` manbadan kelganini snapshotda saqlang.
8. Baholash va qaror yakuni tasdiqlanmasidan oldin xodimga xom eʼlon qilinadigan maʼlumotlar va maxfiy dalillar tegishli privacy siyosatiga mos bo‘lsin.

## Ishchi guruh (real dalillar shart)

Yangi jadval taklifi:

- `BonusWorkingGroup`: maktab, davr, tasdiqlash buyrug‘i, o‘zgarmas versiya, ochilgan/yopilgan sana.
- `BonusWorkingGroupMember`: xodim/fuqaro ID yoki tasdiqli vakil, manzil/kategoriya, tayinlash sanasi, yuridik aʼzolik asosi, `active`.
- `BonusMeeting`: real aʼzolar, yig‘ilish sanasi, kun tartibi, bayonnoma, hujjat sifati, status.
- `BonusAttendance`, `BonusVote`: qaysi aʼzo qatnashgan va qanday ovoz bergan, COI bo‘lsa chetlashganligi. Agar normativ ovoz sir saqlanishini talab etsa, natija hisobini privacy-preserving strukturada olib boring.
- `BonusDecision`: qaysi `assessment`, qaysi `meeting`, qaysi qaror/foiz/summa, direktor buyrug‘i, imzo, `effective_from/to` va revision.

MVP `group_member_count`, `attendees`, `votes_for`, `votes_against`, `votes_abstain`, ba'zi vakillarning borligi va bayonnoma raqamini tekshiradi. U **real aʼzolar yoki individual ovozlarni tekshirmaydi**. Shu sababli haqiqiy 823 tasdiq workflowi emas, uning prototipi.

## Ishchi guruh tasdiqlash bosqichlari

1. Kadrlar/davr/tarif/staff snapshot tasdiqlangan.
2. Mezonlar, ballar va dalillar kiritilgan; baholash muallifi qayd etilgan.
3. Tekshiruvchi soxta/yaroqsiz/eskirgan dalilni rad eta oladi.
4. Guruh tarkibi va majlisga vakolat/yig‘ilish parametrlari normativga mos tekshirilgan.
5. Qatnashuv/kvorum/ovoz natijasi haqiqiy; manfaatlar to‘qnashuvi bo‘lgan shaxs o‘z bahosini tasdiqlamaydi.
6. 50% va fond limiti *bir tranzaksiyada*, parallel tasdiqlarga chidamli tekshiriladi.
7. Tegishli rasmiy qaror va direktor buyrug‘i rekvizitlari kiritilgan (elektron imzo ruxsat bilan).
8. Yakuniy assignment/tolov fayli moliyachiga **eksport uchun tayyorlanadi**, avtomatik UzASBO ga ruxsatsiz yuborilmaydi.

## Maxsus ustamalar

Metodbirlashma rahbari, murabbiy/mentor, sport, rahbar va o‘rinbosar KPI, musiqiy/cholg‘u mahorati, `Zakovat` koordinatori, mukofot/moddiy yordam kabi turlar **alohida `AwardType/Policy`** orqali, sanasi/chegarasi/lavozimi/istisno to‘liq tekshirilgandan keyin ishlatilsin. Hamma turga standard `bonus_rate` qo‘llash xato. Har bir maxsus tur uchun naqd pul manbasi va davr ajratilsin.

## Xatolar va ruxsatlar

- Fond yetmasa: tasdiq `409 Conflict`/form error, kim/qancha/nega ko‘rsatiladi, hamma yozuvlar o‘zgarishsiz.
- Kvorum/real aʼzolik dalili yo‘q: `manual_review_required`.
- 50% limiti oshsa: tasdiq yo‘q, hisob qayta ko‘rib chiqilsin; xodimni yashirin ro‘yxatdan chiqarish yo‘q.
- `district_admin`: ishchi guruhning ovozi va yakunini belgilay olmaydi; aggregate reporting alohida ruxsat siyosati bilan.
- `school_admin`: mezon dalillarini tayyorlashi mumkin, **bir shaxsli grant** yo‘q.
- `bonus_committee`: rasmiy a'zolik tekshirilmasdan yakuniy grant vakolati berilmasin.
- Tegishli `BonusPeriod.school_id` har endpointda tekshirilsin.

## Majburiy testlar

- 0/64/65/76/86/96/100 kabi chegara ballarini **amaldagi** ilova foizlari bilan testlash.
- Talabga mos bo‘lmagan xodim turi/ruxsatli bo‘lmagan bonus sxemasi rad etilishi.
- 1, 2, 3, 5, 7 aʼzo, 2/3 kvorum va noto‘liq maxsus vakillik uchun rad etish (aniq meʼyorni manbadan tekshirib kodga qo‘ying).
- O‘z bahosini o‘zi tasdiqlash, dalilsiz ball, boshqa maktab yig‘ilish IDsi, muddatdan tashqari sanalar bloklanishi.
- 50% chegara va 0/aniq limit/oraliq limit / ikkitadan bir vaqtning o‘zida grant.
- `float` pul xatosi yo‘q; audit/ledger oldingi versiya bilan qoladi.
- Yangi qaror o‘tgan yil bonuslariga retrospektiv taʼsir qilmaydi.

Rasmiy huquqiy talqin noaniq bo‘lsa operatorga manba va nomaʼlum shartni ko‘rsating; yakuniy tasdiqlashni bloklang.
