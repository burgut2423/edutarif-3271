# Test rejasi — AI agentlar uchun

## Baseline (mavjud)

- `pytest -q` — 2026-11-19 holatida 10 ta birlik/integratsion MVP test mavjud. Bu har qanday yangi branchda haqiqiy run bilan qayta tekshirilishi shart.
- `python -m compileall -q app tests`
- Test fayllar: `tests/test_rules.py`, `tests/test_http.py`, `tests/test_bonus_http.py`; fixture: `tests/conftest.py`.
- Github Actions: `.github/workflows/tests.yml`; CI holatini agent tekshiradi, mahalliy natijani CI natijasi deb ko‘rsatmaydi.

## Har bir task uchun test (minimum)

1. **Happy path:** haqiqiy rol va to‘g‘ri input bilan xohlangan natija.
2. **Validation:** manfiy, 0, juda katta, noto‘g‘ri sana, invalid choice, nomaʼlum obyekt.
3. **Authorization:** autentifikatsiyasiz, noto‘g‘ri rol, maktablararo cross-tenant ID, boshqa xodim nomidan so‘rov.
4. **Conflict:** duplicate code, dublikat fan, dublikat request, parallel approval (PostgreSQL testlari).
5. **History/audit:** o‘zgargan entity uchun audit yozuvi; old-state/history qoladi.
6. **Year/policy:** avvalgi o‘quv yili taʼsiri yo‘q; yangi policy eski tasdiqlangan qarorni yashirin o‘zgartirmaydi.
7. **UI:** valid/invalid form feedback, CSRF hidden token, barcha rollarda nav menyu, o‘qituvchi ekranida maxfiy maʼlumot yo‘q.

## Test sinflari

### A. District & onboarding

- District admin maktab kod/nom/language yaratadi, maktab admin login bilan kira oladi.
- Duplicate code va username serverda bloklanadi.
- `school_admin` boshqa school adminini yaratmaydi / tuman admin menyusini ocha olmaydi.
- Disabled school accountlar kirishi va mutatsiya qilishi bo‘yicha siyosat; hozirgi kodda nuqson bo‘lsa alohida issue.

### B. Kadrlar & malaka

- Xodimga fan faqat maktab/academic-year doirasida beriladi.
- Boshlang‘ich metodika / qualification valid until / predmet mosligi.
- Bir xodim ikki maktabda o‘rindosh bo‘lsa modellashtirish/yuklama qoidasi (future).
- Hujjat expires, revoked, no source, duplicate, not verified, appeal.

### C. O‘quv reja & 3271

- Grade 1..11, til varianti, o‘quv reja versiyasi, subject hours vs total hours.
- Guruhga bo‘lish shartlari, 1/2/3+ guruh, maxsus istisno manual review.
- Priority order, valid certificate, re-training equivalence, tie distribution.
- 18/20 o‘quv va 18/16 pedagogik segment, aralash sinflar, 1.5 ekvivalent, to‘liq yillik 2322 soat.
- `transfer` / `swap` full/partial, consent, class/council, optimistic lock, double spend.

### D. 823

- Har criterion `score` oralig‘i, evidence required, scheme per job, score total.
- Fond cheklovi `Decimal`, 50% pedagog count va maxsus istisnolar.
- Kvorum, vakillar, conflict of interest, ovozlar, bayonnoma, direktor buyrug‘i, revocation/re-approval.
- Ikki parallel committee grant 50% yoki fond limitini buzmaydi.

### E. Security

- CRUD IDOR barcha route, CSRF mutatsiya, session expiry, no PII leaks in exports, CSV formula injection, upload sanitization, audit tamper.

## Test maʼlumotlari

- 2 tuman (agar multi-district qamrov qo‘shilsa), 3 maktab, 2 o‘quv yili (2025/2026, 2026/2027), har maktabda 1/4/5/11-sinf, ta'lim tili variantlari.
- 20 ta sintetik o‘qituvchi: malaka toifalari, muddati o‘tgan sertifikat, qayta tayyorlash, o‘rindosh, boshlang‘ich metodika yo‘q.
- 823 uchun 3/4/5/10 pedagog, juft/toq 50% limit; 7/9 aʼzoli guruh, bir nechta baho va fond cheklovi.
- Test uchun PII faqat `Test O‘qituvchi 01` kabi to‘qima yozuv, haqiqiy maʼlumot emas.

## CI va qabul mezoni

- Har PRda unit+HTTP regression (PostgreSQL sinovi qo‘shilmaguncha baholash cheklanganligini yozing).
- Har xavfsizlik yoki normativ tuzatish regressiya testi bilan birga.
- `skip`/`xfail` ishlatilsa sabab va issue; testni yashirin o‘chirish taqiqlanadi.
- CI yashil bo‘lsa ham huquqiy ekspertiza alohida bosqich; bir-birining o‘rnini bosmaydi.
