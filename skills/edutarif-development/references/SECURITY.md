# Security & privacy checklist — majburiy

**Context:** maktab xodimlari to‘g‘risidagi maʼlumotlar, mehnat yuklamasi, sertifikat, ish haqi, dalil va moliyaviy qarorlar maxfiy bo‘lishi mumkin. PII yoki real parolni GitHub issue, CI log, screenshot, test fixture va AI promptga kiritmang.

## Mavjud himoya (tekshirilishi kerak)

- `app/security.py` da PBKDF2-SHA256 hash, signed session cookie, CSRF, current_user, rol va maktab helpers.
- Ayrim HTTP controllerlarda school-scoped fetch va audit.
- `.env.example` namunaviy muhit sozlamalari; `.gitignore` da `.env`, DB, pycache.

**Bu holat butun loyihaning production xavfsizligini isbotlamaydi.** Biror route qo‘shilganda o‘z testi zarur.

## Majburiy xavfsizlik qoidalari

1. **Barcha ID larni tekshirish:** `user.school_id`, `employee.school_id`, `class.school_id`, `curriculum_line.klass.school_id`, `assessment.period.school_id`, `meeting.period.school_id`, `decision.school_id`. Do not trust `school_id` form param. Foreign-key route value avtomatik authorization emas.
2. **Atribut/field darajasida ruxsat:** `teacher` o‘z yuborgan/olayotgan requestini ko‘radi; boshqa xodimning ish haqi, sertifikati, boshqa ustamasi, hujjati ko‘rinmaydi. Hisobotda aniq shaxsiy maʼlumotni minimal ko‘rsating.
3. **Mutatsiya = CSRF + rol + school-scope + server-side validation + audit.** GET hech narsa o‘zgartirmasin.
4. **Session:** HTTPS (`COOKIE_SECURE=true`), SameSite, HttpOnly, session expiry va invalidation, parol almashganda eski sessiyani bekor qilish, account disable, logout.
5. **Parol:** kuchli maxfiy parol, login rate-limit, lockout/alert, 2FA, forgot/reset token faqat vaqtli/bir martalik. Password logga yozilmasin.
6. **Upload:** faqat ruxsatli fayl format/hajm, MIME va magic-byte tekshirish, malware scan, private object storage, signed download, antivirus/retention. Hujjat URLni `javascript:`ga ochmang.
7. **Output:** Jinja autoescape, user input escaping, CSV/Excel formula injection (`=`, `+`, `-`, `@` bilan boshlangan qiymat) oldini olish, content security policy.
8. **DB:** SQLAlchemy bind param; unique/FK/check constraints, o‘quv yili va maktab bo‘yicha indeks, PG Row-Level Security ehtimolini baholash. Lock bilan parallel approval race ni to‘xtatish.
9. **Secrets:** `.env`/API kalit/password/real PII bilan commit qilmaslik. CI secret scanning, dependency scan va token rotation, storage encryption/backup. Test fixture synthetic.
10. **Audit:** kim/qachon/nimani/nimadan nimaga, old/new snapshot, failed attempt, export/download/approver, retention. Audit log o‘chirilmas yoki maxsus vakolat bilan qo‘riqlanadigan bo‘lsin.
11. **Data protection:** milliy va ichki qonun talabini yuridik tekshirish, minimizatsiya, retention, mas'uliyat, foydalanuvchi roziligi va ruxsatlar. O‘quvchilar to‘g‘risidagi ma'lumotlar iloji boricha agregat son bo‘lib qolsin.
12. **Emergency:** backup restore tested, disaster recovery, operator rollback, audit integrity, monitoring/alert, access review.

## Multi-tenant sinov matriksi

| Actor | Resource/Action | Kutilgan |
|---|---|---|
| School A admin | School A staff / class / allocation update | Ruxsat |
| School A admin | School B staff / class / grid / allocation / council / request update | 403/404, o‘zgarish yo‘q |
| School A committee | School B bonus assessment / meeting | 403/404 |
| Teacher A | Teacher B paroli, oylik maoshi va shaxsiy ustamasi | Rad |
| Teacher A | O‘zining yuborgan yoki o‘zi oluvchi bo‘lgan requesti | Ruxsatga ko‘ra |
| Teacher A | Boshqa xodim nomidan consent | Rad |
| District admin | School creation | Ruxsat |
| District admin | 823 workgroup decision approve | Rad |
| Disabled account | Istalgan private route | Rad |
| Unauthenticated | Istalgan private route | Login/401 |

## Release gate (production oldidan)

Alembic migratsiyalari, PostgreSQL concurrency testlar, authenticated session security, rate limiting, PII minimizatsiyasi, backups, dependency audit, monitoring, malware scan, huquqiy ekspertiza, yakuniy penetration test va rasmiy integratsiya vakolati bo‘lmaguncha **production-ready** deb belgilanmasin.
