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
python -m scripts.bootstrap_admin
uvicorn app.main:app --reload
```

Brauzer: `http://127.0.0.1:8000`. Birinchi kirishda vaqtinchalik admin parolini yangilang.

Linux/macOS: `python3 -m venv .venv && source .venv/bin/activate`,
`cp .env.example .env` va shu buyruqlardan foydalaning.

### PostgreSQL

Ishlab chiqarish uchun `DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/edutarif`.
`python -m scripts.init_db` jadvallarni birinchi marta yaratadi. Alembic migratsiyalari
hozircha yo‘q; production maʼlumotlarida `create_all` ni migratsiya o‘rnida ishlatmang.

Docker Compose uchun `.env`da `POSTGRES_PASSWORD` va yuqoridagi maxfiy sozlamalar,
`docker compose up -d --build`, keyin `docker compose exec web python -m scripts.bootstrap_admin`.

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
- `scripts/` — boshlang‘ich maktab maʼlumotnomalari va administrator yaratish.
- `docs/REGULATIONS.md` — normativ xarita, kamchilik va bosqichlar.
- `tests/` — dastlabki unit / HTTP testlar.

## Xavfsizlik

PBKDF2 SHA-256 (420,000 iteratsiya), imzolangan sessiya cookie, CSRF, rol va maktab
chegarasi tekshiruvlari, audit mavjud. HTTPS bilan `COOKIE_SECURE=true` qo‘ying.
Login rate-limit, 2FA, maxfiy hujjatlar uchun server-side fayl saqlash, backup,
maʼlumotlarni himoya qilish / data retention, integratsiya ruxsatlari, migratsiyalar,
PostgreSQL tranzaksiya blokirovkalari hamda to‘liq pen-test **production oldidan zarur**.

Hech qachon `.env`, haqiqiy xodim maʼlumotlari va foydalanuvchi parollarini GitHub'ga yuklamang.

## GitHub

Bu arxiv yangi repositoryga push qilishga tayyor. GitHub'da bo‘sh PRIVATE repository
(`edutarif-3271`) oching, so‘ng:

```bash
git init
git add .
git commit -m "Initial EduTarif MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/edutarif-3271.git
git push -u origin main
```

Agar GitHub login bilan HTTPS token talab qilsa, GitHub CLI yoki credential manager bilan
standart autentifikatsiyadan foydalaning; parollarni chatga yubormang.

## Test

`pytest -q`

## Normativ manbalar

- https://lex.uz/acts/-4919258 (3271, 3271-1, 2026-08-01)
- https://lex.uz/docs/-4532496 (823 va o‘zgarishlar)
- https://lex.uz/acts/-8584243 (2026-11-11, 617-son qaror)
- https://lex.uz/uz/acts/-7793627 (3271-1)
- MMTV 10.04.2026, 133-son buyruq — 2026/2027 o‘quv yiliga mo‘ljallangan tayanch o‘quv reja.
