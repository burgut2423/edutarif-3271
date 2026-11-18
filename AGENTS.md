# EduTarif 3271/823 — AI agentlar uchun loyiha qoidalari

> Bu hujjat **barcha kod yozuvchi AI agentlarga** (GitHub Copilot, Codex, Claude Code, Cursor va boshqalar) tegishli. Agent vazifani boshlashdan oldin ushbu faylni to‘liq o‘qishi shart.

## Vazifa va yakuniy maqsad

O‘zbekiston umumta'lim maktablarida o‘quv reja, sinf komplekti, pedagog kadrlar, 3271-son nizom bo‘yicha dars soatlarini **qonuniy va shaffof taqsimlash**, 823-son qaror bo‘yicha direktor jamg‘armasi ustamalarini baholash va rasmiy tasdiqlashga xizmat qiladigan **ko‘p maktabli** web platforma. Dastur *tavsiya, tekshiruv, hujjatlashtirish* qiladi; pedagogik kengash va ishchi guruh vakolatini o‘zlashtirmaydi.

## Ishni boshlash: o‘qish ketma-ketligi

1. `README.md` — ishga tushirish, holat.
2. `docs/AI_HANDOFF.md` — **hozirgi holat, qilinmagan ishlar, navbatdagi sprint**.
3. `skills/edutarif-development/SKILL.md` — batafsil agent protokoli.
4. Tegishli yo‘nalishdagi `skills/edutarif-development/references/*.md`.
5. `docs/REGULATIONS.md` va yangilangan rasmiy Lex.uz matnlari — faqat huquqiy kod o‘zgarsa.
6. Kodni **o‘qib chiqing**, taxmin asosida fayl/funksiya/endpoint yaratilgan deb o‘ylamang.

## Texnologiyalar va asosiy yo‘llar

- Python 3.12, FastAPI, SQLAlchemy 2.x, Jinja2, Bootstrap 5.3, PostgreSQL ishlab chiqarishda va SQLite testlarda.
- `app/models.py`: SQLAlchemy ORM va munosabatlar.
- `app/controllers/{auth,district,school,teacher,bonus}.py`: HTTP handlerlar.
- `app/services.py`: vaqtinchalik 3271/823 biznes qoidalari. Murakkab hisoblagichlarni kichik, testlanadigan servislar bo‘yicha ajrating.
- `app/security.py`: login, CSRF, foydalanuvchi/rol/maktab doirasi.
- `app/templates/`, `app/static/`: sahifalar va stil.
- `tests/`: regressiya testlari. `.github/workflows/tests.yml`: CI.
- `docs/REGULATIONS.md`: amaldagi talablarga moslik xaritasi.

## O‘zgartirib bo‘lmaydigan prinsiplar

1. **Multi-tenancy:** har bir maktabga tegishli CRUD/query/eksport/so‘rov/action `school_id` doirasi tekshiruvisiz amalga oshmasin. Foreign key ID ni URL/formada berish huquq bermaydi. Test: A maktab B maktabning har bir obyektiga kira olmaydi.
2. **Rollar va vakolatlar:** `district_admin` maktab/umumiy katalogni boshqaradi, **823 ishchi guruhning qarorini tasdiqlamaydi**; `school_admin` maktab kadr/setka/loyihalarni boshqaradi, ustamani yolg‘iz o‘zi tasdiqlamaydi; `teacher` faqat o‘z yuklamasi va so‘rovlarini ko‘radi; `bonus_committee` vakolati haqiqiy ishchi guruh a'zoligi va manfaatlar to‘qnashuvi asosida qayta tekshirilishi kerak.
3. **3271 ≠ 823:** dars taqsimoti va rag‘batlantirish ikkita mustaqil workflow; alohida ledger, audit va tasdiqlash qoidalari.
4. **Rasmiy manba:** normativni faqat Lex.uz yoki tegishli vakolatli idora hujjati va amal qilish sanasi bilan kiritish. Normalangan qoidalar versiyalansin. Qonuniy talqin bahsli bo‘lsa `review_required` holatida to‘xtatilsin; default avtomatik tasdiqlash yo‘q.
5. **1–4 / 5–11 alohida:** haftalik bir stavka o‘quv yuklamasi mos ravishda 18 va 20 soat, pedagogik yuklama mos ravishda 18 va 16. Yillik 1.5 stavka/2322 soatni to‘liq tasdiqlash uchun alohida yillik kalendar va hisob talab qilinadi. Hozirgi `used_rate` faqat **taxminiy stavka** hisobidir.
6. **O‘quv yiliga moslik:** sinf, setka, tarifikatsiya, o‘tkazish so‘rovi, ustama va hujjat tegishli o‘quv yili/davriga bog‘lanadi. Tarixiy maʼlumot o‘chirilmaydi; tasdiqlangan natija snapshot/versiya bilan saqlanadi.
7. **Adolat:** bir xil yuridik ustuvorlikka ega shaxslar uchun hujjatlashtirilgan tenglik mezoni; algoritm tavsiya chiqaradi, asoslangan istisno va yozma rozilik alohida qayd etiladi. Hech qachon yashirin qoida/tasodifiy tartib asosida soat tarqatmang.
8. **Moliyaviy aniqlik:** pul va ustama foizi uchun `Decimal`/`Numeric`, pulda `float` ishlatmang; yil/davr limiti, bosh hisob va alohida istisnolarni testlang.
9. **Audit va tranzaksiya:** hujjat/rol/soat/qaror/ustama o‘zgarsa actor, vaqt, school, old/new values va manba saqlansin. Bir tranzaksiyada mos keluvchi holatlar yangilansin; ikkita agent bir vaqtda tasdiqlasa poyga holati oldini olinsin.
10. **Maxfiylik:** shaxsiy xodim/o‘quvchi maʼlumoti, parol, token, hujjat, `.env`, real DB yoki backup GitHub'ga hech qachon kirmasin. Sinovda sintetik maʼlumotdan foydalanilsin.
11. **Ishlab chiqarishga tayyorlikni asossiz eʼlon qilmang.** MVP — ish jarayoni prototipi; to‘liq yuridik/axborot xavfsizligi/moliya tekshiruvlarisiz haqiqiy to‘lov yoki rasmiy tarifikatsiya yaratish mumkin emas.

## Agentning majburiy ish tartibi

1. `git status --short`; `git log -5 --oneline`; kodni va testlarni ko‘ring.
2. `python -m pytest -q` bilan baseline yarating. Muammo chiqsa sababini yozing; mavjud testlarni yashirin o‘chirmang.
3. `docs/AI_HANDOFF.md` dan **bitta aniq vazifa** oling, yoki foydalanuvchi bergan aniq vazifani bajaring. Yirik modullarni bo‘lak PRlarga ajrating.
4. Qo‘shiladigan biznes qoidaning normativ manbasi, amal qilish sanasi, qoidaning boshqaruvchi roli, istisno va rad etish sabablarini belgilang.
5. Minimal sxema + servis + controller + view + test + audit + migratsiya (sxema o‘zgarsa) yarating. Barcha o‘zgarishlarda maktablararo ruxsat sinovini kiriting.
6. `python -m pytest -q`; imkon bo‘lsa `python -m compileall -q app tests` va linter/type-check. Test o‘tmasa *muvaffaqiyat* demang.
7. PR/commitga: o‘zgargan fayllar, ta’sirlangan role/endpoint, test natijasi, xavf va hali ishlamaydigan qismlarni yozing.
8. `docs/AI_HANDOFF.md` dagi *Done / Next / Blockers / Latest change* bo‘limlarini yangilang. Qisqa, faktga asoslangan yozing.
9. Repo egasining mavjud fayllarini o‘chirib yubormang; maxsus ruxsatsiz rewrite, rebase, force-push, prod migrations, credentials yoki tashqi xizmatlarga yozish yo‘q.

## Qabul mezonlari (Definition of Done)

- Vazifa acceptance criteria barcha jihati bajarilgan; testlar yozilgan/o‘tgan.
- Foydalanuvchi roliga mos UI bor; mobil/desktopda xatolar yo‘q.
- Maktablararo IDOR tekshiruvlari va CSRF qo‘llangan; pul, yil va qonuniy limitlar tekshirilgan.
- Har bir tasdiqlash saqlangan hujjat/audit bilan bog‘langan; avvalgi qaror tarixda qolgan.
- `docs/AI_HANDOFF.md` va tegishli skill/reference fayl zarur bo‘lsa yangilangan.
- Fakt yoki talqin tasdiqlanmagan bo‘lsa natijada ochiq qayd etilgan.

**Agent uchun birinchi navbatdagi vazifalar va aniq test ssenariylari:** `skills/edutarif-development/references/BACKLOG.md` va `TEST_PLAN.md`.
