# EduTarif 3271 / 823 — tuman va maktablar uchun web ilova

FastAPI + SQLAlchemy + Jinja2 / Bootstrap 5.3. 1–11-sinf dars soatlari setkasi,
3271 bo‘yicha ustuvorlik asosida **taklif** berish, o‘qituvchilar orasida yuklama
o‘tkazish/almashtirish so‘rovi va 823 direktor jamg‘armasi hisobi.

> **Holat: ishlaydigan MVP, yakuniy davlat tarifikatsiyasi yoki moliyaviy tizim EMAS.**
> Qoidalarni ishlab chiqarishga tatbiq qilishdan oldin yuridik va buxgalteriya ekspertizasi,
> 2026/2027 fan-by-sinf tayanch o‘quv rejasi, 823 ilovalar mezonlari, 1–4 metodikasi,
> guruhlarga bo‘lish, ishchi guruh tarkibi, davlat integratsiyalari va maʼlumotlarni himoya
> qilish tekshiruvi talab etiladi.

## Ishga tushirish (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# .env faylida SESSION_SECRET (64+ tasodifiy belgi) va BOOTSTRAP_PASSWORD ni almashtiring
python -m scripts.db_migrate  # Alembic migration
python -m scripts.bootstrap_admin
uvicorn app.main:app --reload
```

Brauzer: `http://127.0.0.1:8000`. Birinchi kirishda vaqtinchalik admin parolini yangilang.

Linux/macOS: `python3 -m venv .venv && source .venv/bin/activate`,
`cp .env.example .env` va shu buyruqlardan foydalaning.

### PostgreSQL

Ishlab chiqarish uchun `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/edutarif`.
`python -m scripts.db_migrate` yoki `alembic upgrade head` sxemani
Alembic orqali yaratadi. `python -m scripts.init_db` faqat **development**
uchun namunaviy tuman, fanlar, yil va taxminiy policy qiymatlarini qo‘shadi;
rasmiy fan-soat rejasini bermaydi. `python -m scripts.bootstrap_admin` migratsiyani
yana tekshiradi va administratorni yaratadi (fuqarolarning real maʼlumoti yo‘q).
**Eski `create_all()` bazasi avtomatik upgrade qilinmaydi**: zaxira nusxasi,
`python -m scripts.schema_report` va operator tomonidan schema parity auditdan
keyingina `alembic stamp 20261119_01` qo‘llansin. Tafsilotlar: `docs/DB_SCHEMA.md`.

Alohida ajratilgan bo‘sh PostgreSQL sinov bazasida migratsiyani tekshiring,
keyin production deploymentdan avval `alembic upgrade head`ni alohida release
bosqichida ishlating. `downgrade base` **barcha jadvallarni o‘chiradi**: hech
qachon haqiqiy bazada sinov maqsadida ishlatmang.

Docker Compose uchun `.env`da `POSTGRES_PASSWORD` va yuqoridagi maxfiy sozlamalar,
`docker compose up -d --build`, keyin `docker compose exec web alembic upgrade head` va
`docker compose exec web python -m scripts.bootstrap_admin`.

## Rollar

- `district_admin`: yangi maktab, maktab adminlari, fan katalogi, yil, audit; **823 ishchi guruhi qarorlariga aralashmaydi**.
- `school_admin`: xodimlar, sinflar, setka, soat taqsimoti, kengash bayonnomasi, arizalar; ustama uchun dastlabki baholash.
- `teacher`: o‘z tasdiqlangan darslarini/ustamalarini ko‘radi; soat o‘tkazish yoki almashtirish so‘rovini yuboradi va qabul qiluvchiga kelgan so‘rovni tasdiqlaydi.
- `bonus_committee`: ishchi guruh majlisi maʼlumotlari asosida ustama bahosini tasdiqlaydi. Bu rolga ega hisobning mavjudligi ishchi guruhning **haqiqiy tarkibi tekshirilganini anglatmaydi**.

## Ish jarayoni

1. Tuman admin maktab va administratorini yaratadi. Login parollari har maktab uchun alohida.
2. Maktab admin xodimlarni va ularning fan/malaka hujjatlarini kiritadi.
3. Sinflar (1–4, 5–11) va fanlar kesimida haftalik soat/guruh setkasi kiritilib tekshiriladi.
4. Soatlar ustuvorlik bo‘yicha teng taqsimlanishi haqida dastlabki tavsiya beriladi.
5. Maktab admin dars soatlarini loyihalashtirib, pedagogik kengash bayonnomasi bilan tasdiqlaydi; maktab kesimida CSV eksport qiladi.
6. O‘qituvchi o‘z soatini ko‘radi, o‘tkazish yoki almashtirish so‘rovini yuboradi.
7. Qabul qiluvchi roziligi + pedagogik kengash qarori bilan maktab admin so‘rovni rasmiylashtiradi.
8. 823 bo‘yicha davr, ishchi guruh, ballar, bayonnoma, kvorum, ovozlar,
   jamg‘arma limiti va pedagoglarning 50% miqdori nazorat qilinadi.

## Asosiy papkalar (MVC)

- `app/models.py` — SQLAlchemy maʼlumotlar modeli, FK va cheklovlar.
- `app/controllers/` — HTTP controllerlar (auth, district, school, teacher, bonus).
- `app/services.py` — 3271 ustuvorlik, stavka va 823 foiz / fond hisoblash biznes qoidalari.
- `app/templates/` — adaptiv AdminLTE uslubidagi Bootstrap sahifalar (server rendered view).
- `app/security.py` — parol xeshlash, session, CSRF va kirish huquqlari.
- `scripts/` — Alembic migratsiyasi, development seed va administrator yaratish.
- `migrations/` — review qilinadigan versiyali database schema.
- `docs/DB_SCHEMA.md` — ER skelet va eski baza xavfsiz ko‘chirish.
- `docs/UI_WIREFRAMES.md` — maketlar va dashboard dizayn spetsifikatsiyasi.
- `docs/REGULATIONS.md` — normativ xarita, kamchilik va bosqichlar.
- `tests/` — dastlabki unit / HTTP testlar.

## Xavfsizlik

PBKDF2 SHA-256 (420,000 iteratsiya), imzolangan sessiya cookie, CSRF, rol va maktab
chegarasi tekshiruvlari, audit mavjud. HTTPS bilan `COOKIE_SECURE=true` qo‘ying.
Login rate-limit, 2FA, maxfiy hujjatlar uchun server-side fayl saqlash, backup,
maʼlumotlarni himoya qilish / data retention, integratsiya ruxsatlari, migratsiya deploy nazorati,
PostgreSQL tranzaksiya blokirovkalari hamda to‘liq pen-test **production oldidan zarur**.

Hech qachon `.env`, haqiqiy xodim maʼlumotlari va foydalanuvchi parollarini GitHub'ga yuklamang.

## GitHub

Joriy Private repository: `https://github.com/burgut2423/edutarif-3271`.
Clone qilish:

```bash
git clone https://github.com/burgut2423/edutarif-3271.git
cd edutarif-3271
```

Repo mavjud; yangi bo‘sh repository yaratish kerak emas. GitHub tokenlarini
chatga yoki `.env`ga kod bilan birga commit qilmang.

## Test

`pytest -q`

## Normativ manbalar

- https://lex.uz/acts/-4919258 (3271, 3271-1, 2026-08-01)
- https://lex.uz/docs/-4532496 (823 va o‘zgarishlar)
- https://lex.uz/acts/-8584243 (2026-11-11, 617-son qaror)
- https://lex.uz/uz/acts/-7793627 (3271-1)
- MMTV 10.04.2026, 133-son buyruq — 2026/2027 o‘quv yiliga mo‘ljallangan tayanch o‘quv reja.

## AI agentlar uchun davom ettirish skill'i

Loyiha boshqa AI agentlar (Codex, Claude Code, Cursor, GitHub Copilot va boshqalar) ishni
izchil davom ettirishi uchun alohida hujjatlar bilan taʼminlangan:

- **`AGENTS.md`** — barcha AI agentlar uchun majburiy xavfsizlik, biznes va workflow qoidalari.
- **`skills/edutarif-development/SKILL.md`** — asosiy portable skill (YAML frontmatter va bosqichma-bosqich protokol).
- **`skills/edutarif-development/references/`** — 3271, 823, arxitektura, test, xavfsizlik, integratsiya, UX/workflow va backlog.
- **`docs/AI_HANDOFF.md`** — keyingi agentga aniq holat, bajarilmagan ishlar va tayyor start prompt.
- **`CLAUDE.md`, `GEMINI.md`, `.cursor/rules/edutarif.mdc`, `.claude/skills/edutarif-development/SKILL.md`, `.github/copilot-instructions.md`** — turli agentlarning avtomatik kirish fayllari.

Agentga boshlash topshirig‘i: *`AGENTS.md` va `docs/AI_HANDOFF.md` ni o‘qi,
`skills/edutarif-development/SKILL.md` ga amal qil, birinchi P0 taskni test bilan bajar.*
Skill huquqiy ekspertiza yoki haqiqiy moliyaviy tasdiq o‘rnini bosmaydi.