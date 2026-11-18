## Task ID / maqsad

<!-- Masalan: P0-02 / cross-school IDOR -->

## O‘zgargan funksiyalar

<!-- models / migrations / services / controllers / views / docs -->

## Normativ manba va kuchga kirgan sana (agar tegishli bo‘lsa)

<!-- URL, band, effective date, manba tasdiqlovchi, yoki N/A -->

## Ruxsat, maxfiylik, tenant, audit

- [ ] Rol va maktab (`school_id`) serverda tekshirildi.
- [ ] Xodimning faqat o‘z maʼlumoti (teacher ownership) tekshirildi.
- [ ] CSRF / input validation / audit qo‘shildi yoki N/A asoslandi.
- [ ] PII, `.env`, secrets, real DB commit qilinmadi.
- [ ] Migratsiya va rollback ko‘rib chiqildi.

## Test / natija

```text
python -m pytest -q
# Paste real output
```

## Hujjatlar / handoff

- [ ] `docs/AI_HANDOFF.md` yangilandi.
- [ ] Kerak bo‘lsa skill reference/README yangilandi.

## Cheklovlar va xavflar

<!-- Tasdiqlanmagan huquqiy talqin, rasmiy integratsiya, cybersecurity, concurrency ... -->
