# 3271 — sinf komplekti, setka, dars taqsimoti va tarifikatsiya

**Asosiy manba:** https://lex.uz/acts/-4919258 (30.06.2020 ro‘yxatdan o‘tgan 3271-son nizom va konsolidatsiya).
**2026-yilga aloqador o‘zgarish:** https://lex.uz/uz/acts/-7793627 (3271-1, 28.10.2025, 15-banddagi yangi tartib 01.08.2026 dan).
**O‘quv reja:** 2026-yil 10-apreldagi 133-son buyruq va uning 2026/2027 o‘quv yilidagi til/tur variantlari. **Rasmiy matn + tegishli ilovani yuridik/sohaviy tasdiqlamasdan prod qoidaga aylantirmang.**

## Huquqiy klassifikatsiya

- **Normativ**: qonunda belgilangan sanalar, lavozimga moslik, ustuvorlik, dars/mehnat yuklama limitlari va hujjatlar; aynan mos amal qilish davri bilan.
- **Tekshirish uchun tavsiya**: algoritm taklif qilgan xodim/soatlar. Rasmiy vakolatli yig‘ilish tasdiqlamay turib `draft/recommended` holatida.
- **Maktabning inson qarori**: pedagogik kengash tavsiyasi, izoh, teng sharoit, yozma rozilik, zarur kelishuv va hujjat.
- **Istisno**: kam komplektli, inklyuziv, filial, tillar aralash sinf, individual/uyda taʼlim, vaqtinchalik xodim, dekretdan qaytish, o‘rindoshlik va boshqa holatlar. Faqat normativ manba bilan.

## 1–4 va 5–11 alohida hisob

| Turi | 1–4-sinf | 5–11-sinf |
|---|---:|---:|
| 1 stavka haftalik o‘quv yuklamasi | 18 soat | 20 soat |
| 1 stavka haftalik pedagogik yuklama | 18 soat | 16 soat |
| Haftalik pedagogik koeffitsiyent | 1.0 | 0.8 |
| Malaka/taʼlim mosligi | boshlang‘ich taʼlim mutaxassisligi **yoki** shu fanni boshlang‘ichda o‘qitish metodikasi | fan/diplom va hujjatning mosligi |
| Hozirgi kod | `qualified`, `used_rate` grade<=4 | `qualified`, `used_rate` grade>=5 |

MVP `weekly_hours/18` yoki `/20` bilan stavka *ekvivalenti* hisoblaydi. Aralash (bir pedagog ham 4-sinf, ham 5-sinfda ishlasa) ikki segment bo‘yicha hisob hamda yillik pedagogik ish va jadval tekshiruvi talab etiladi. **`annual_workload_estimate` yakuniy huquqiy tarifikatsiya emas**; 2322 soat kabi yillik cheklov kalendar, haftalar, taʼtil, ustama turidagi mehnat va real nizom bandlari bilan mustaqil tekshirilsin. 1.5 stavkani «haftalik jami 30 soat» deb umumiylashtirish xato; sinf darajalari aralashsa ekvivalent hisob kerak.

## Fanlar va setkani modellashtirish

Kirishlar:

1. `academic_year` va normativ versiya (`source_document`, `effective_from`, `approved_by`, `appendix_no`).
2. `school` taʼlim tili, hududi/turi, filial holati, maxsus profil.
3. `class_group`: o‘quv yili, sinf raqami (1–11), harfi, taʼlim tili, haqiqiy o‘quvchi soni, rozilik/kelishuv.
4. `curriculum_template`: sinf/til/turga mos fan ro‘yxati va haftalik soat.
5. `subject_group_rule`: qaysi fan/qaysi sinfda, nechta o‘quvchi bo‘lsa va qanday rasmiy asosda guruhlar soni >1 bo‘lishi.
6. `school_curriculum_line`: `weekly_subject_hours`, `approved_groups`, `teacher_hour_budget`, source/override reason.

Hisob misoli (faqat matematik, yuridik emas): bir sinfning fan haftalik soati 3, huquqiy tasdiqlangan guruh soni 2 bo‘lsa, o‘qituvchi yuklamasi `3*2=6`. O‘quvchining 3 soat fan olishi o‘zgarmaydi. Guruh soni uchun `students >= x` kabi nomaʼlum chegarani kodga **taxminan** yozmang; tegishli normani tekshiring.

## 3271 15-band bo‘yicha ustuvorlik mexanizmi

2026/2027 uchun 15-bandning 2026-08-01 dan kuchga kirgan tahririni tekshiring. Koddagi `PRIORITY_LABELS` taxminiy algoritm xaritasi: oliy toifa; faniga mos tan olingan milliy/xalqaro sertifikat; birinchi toifa; ikkinchi toifa; oliy ma'lumotli toifasiz; qayta tayyorlash diplomi (mazkur banddagi mos hujjatga ko‘ra tegishli teng ustuvorlik); o‘rindosh; pedagogika yo‘nalishi yuqori kurs talabasi; boshlang‘ich uchun o‘rta maxsus/professional ma'lumotli; tegishli mutaxassislikdagi rahbar.

Tekshirilishi shart bo‘lganlar:

- `priority_rank` hujjatning **tegishli fan** bo‘yicha ekanini, sertifikat turi/darajasi va amal qilish muddatini to‘liq tekshirmaydi.
- `priority_basis` ni foydalanuvchi matn sifatida kiritishi o‘z-o‘zidan rasmiy ustuvorlik dalili emas.
- Hujjat qayta tayyorlash diplomi bo‘lsa, tegishli boshqa ustuvor hujjat bilan tenglashish alohida qoida.
- Ustuvorlikning ayrim toifalariga shartli ruxsat bor (masalan, oliy ma'lumotli pedagog yetishmasligi). Bor-yo‘qligi tekshirilishi kerak.
- Bir nechta hujjat bo‘lsa **eng ustuvori** tanlanadi; vaqt jihatidan amal qilmagan hujjat rad etiladi.

### Tenglik va algoritm tavsiyasi

`distribution_preview()` hozir navbat bo‘yicha yarim soat ulushlarda taklif qiladi; bu rasmiy «adolatli taqsimot»ning barcha huquqiy va mehnat tartibini qamrab olmaydi. Taklif algoritmining yangi turi `priority_group + actual existing workload + consent + authorized exception` asosida bo‘lsin, har qadamda *why* (`rule_id`, source, credential, qolgan soat, employee count, tie-breaker) tushuntirishini qaytarsin. Natija tasdiqsiz ishlatilmasin. Teng huquqli ikki pedagogga 5,5/5,5 imkon bo‘lsa tasodifiy 10/1 bo‘linmasin. Chegaraviy 0,5 soat olinganda soni toq bo‘lsa, tanlash sababi aniq auditlansin.

### State machine

`class: draft → checked → approved → archived`

`curriculum: imported → draft → validated → approved → superseded`

`allocation: draft → recommended → council_approved → published → superseded`

**Izoh:** bu taklif etilayotgan to‘liq model. Hozirgi DB da sinf `approved: bool`, setka `verified: bool`, allocation `draft/approved/superseded`; to‘liq holat mexanizmi mavjud emas.

## Tarifikatsiya bo‘yicha hisob chiqarish qoidalari

- Bir davrdagi sinf fanlar soatlari to‘liq bo‘lsin (required/missing); sinf kesimi va fan kesimi bo‘yicha yig‘indi mos bo‘lsin.
- `allocation` jami, sinf/fan setka satri uchun belgilangan `teacher_hour_budget` ni oshirmasin; tasdiqlangan setka tahrirlansa `draft` rejimga qaytishi yoki rasmiy yangi versiya chiqarishi kerak.
- O‘qituvchi **faniga mosligi** va ruxsatli maktab/ish holati bo‘lmasa taqsimot bloklansin.
- Xodim ishga kirgan/chiqqan sanalar, o‘qituvchi taʼtili, kunlar, vaqtinchalik almashish holatlari saqlansin.
- Fan/sinf/taʼlim tili kesimida dalil: qaysi hujjatdan necha soat, qaysi kengash qaroridan keyin kimga biriktirilgan.
- Tarif yakuni: alohida ekranda preview, mismatch, tasdiqlovchi organlar, imzo, fayl va eksport. **Noma'lum qiymatni 0 qilib yashirmang**.

## Qabul testlarining minimumi

1. Oliy toifali (muddati amaldagi) va toifasiz teng bo‘lmagan; muddati o‘tgan toifa ustuvorlik bermasligi.
2. Milliy/xalqaro sertifikat darajasi/fani mos bo‘lmasa taqsimot avtomatik tasdiqlanmasligi.
3. Boshlang‘ich mutaxassisligi yoki metodika yo‘q xodim 3-sinf fanini ololmasligi; tegishli mos xodim olishi.
4. 4- va 5-sinfda ishlaydigan bir xodim uchun 18/20 hisob, yillik yuklama va chegarani alohida tekshirish.
5. Shu fan, shu sinfdagi barcha soatlarning o‘qituvchilarga jami setkadan oshmasligi.
6. A maktab administratori B maktab setkasini ID bilan tasdiqlay olmasligi.
7. Tasdiqlangan soatni almashtirishda rozilik va kengash qarori bo‘lmasa o‘tmasligi; eski qaror tarixda qolishi.
8. O‘tgan yilgi setka yangi o‘quv yiliga «faol» deb noto‘g‘ri qo‘shilmasligi.
9. Parallel ikkita tasdiq bir xil soatni ikki marta sarflamasligi.
10. Normativ istisno manbasiz bo‘lsa `manual_review_required`, noto‘g‘ri `approved` emas.

**Hech qachon:** huquqiy noaniqlikni yashirish, «avtomatik yuridik qaror» chiqarish yoki hujjat/e-imzoni soxtalashtirish.
