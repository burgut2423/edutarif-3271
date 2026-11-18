# Ruxsatli import / eksport va davlat axborot tizimlari

## Asosiy prinsip

**ERP, UzASBO, eMaktab yoki boshqa davlat xizmati bilan integratsiya faqat rasmiy API, vakolat, texnik hujjat va tegishli shaxsiy maʼlumotlarni qayta ishlash ruxsati bo‘lsa amalga oshiriladi.** Credential har bir service account uchun, secret managerda; login-parol yoki cookie sessiyani repositoryga qo‘ymang. Norasmiy API scraping bilan xodimning shaxsiy maʼlumoti/maoshini tortish rejalashtirilmasin.

## Integratsiya yo‘nalishlari

| Yo‘nalish | Kutilgan data | Muhim nazorat | Holat |
|---|---|---|---|
| Xodimlar | xodimning tashkilot, shartnoma, lavozim, fani, toifasi va hujjatlari | mos xodim ID, ruxsat, vaqt, duplicate | Rejalashtirilgan |
| Tayanch o‘quv reja | o‘quv yili, til, sinf, fan, soat, guruhga bo‘lish | rasmiy manba/ilova, versiya va maktab istisnosi | Rejalashtirilgan |
| Tarifikatsiya eksport | maktab, yil, sinf, fan, xodim, yuklama, status | faqat approved snapshot, audit, schema version | CSV prototip; rasmiy format yo‘q |
| UzASBO / payroll | approved ustama, tarif bazasi, davr, fond, buyruq | idempotency, readback, tasdiq, shaxsiy maʼlumotlar | Rasmiy API ruxsati kutilmoqda |
| eMaktab | faqat huquqiy jihatdan ruxsat etilgan statistika | minimizatsiya, data owner, consent | Alohida baholash kerak |

## Import formatlari (taklif)

1. `schools.csv`: `district_code,school_code,school_name,address,language,active`.
2. `employees.csv`: `school_code,external_person_id,full_name,job_title,employment_type,subject_code,valid_from,valid_to`.
3. `classes.csv`: `school_code,academic_year,grade,section,language,student_count,source_document`.
4. `curriculum.csv`: `academic_year,template_code,language,grade,subject_code,weekly_hours,group_rule,source_document,effective_from`.
5. `allocations.csv`: `school_code,academic_year,class_code,subject_code,employee_external_id,weekly_hours,state,decision_ref`.

Bular **proposed schemas**, hozir kodda bunday import yo‘q. Fayl import qilinmasidan oldin schema validatsiyasi, sintetik preview, conflict report, dry-run, admin tasdiq, `row_number:error` hisoboti kerak; yashirin overwrite yo‘q.

## Integratsiya adapter shabloni

- `SourceDocument { issuer, document_number, document_date, effective_from/to, edition, url, file_hash, verified_by }`
- `ImportJob { school_id, source_system, year_id, checksum, state, started_by, imported_count, rejected_count, report_ref }`
- `ExternalMapping { school_id, external_system, external_id, internal_id, valid_from/to }`
- `ExportJob { school_id, year_id, policy_version_id, exported_by, format, checksum, status, remote_ack }`

Sinf/setka/bonus kabi yuridik maʼlumotni import qilgandan keyin `unverified` → `checked` → vakolatli `approved` oqimi o‘tsin. Import ruxsati o‘z-o‘zidan approval emas.

## Dastlabki export talablar

Maktab/yil/sinf/fan/xodim va status, 3271 ustuvorlik izohi, bayonnoma raqami, normativ versiya, imzo, rad sabab, 823 davr/ball/foiz/summa/fond manbasi. CSV/Excel injectionni bloklang; fayl UTF-8/Excel uslubida o‘zbek matnlarini buzmasin.

## Ishlab chiqarishdan oldin tashqi tomon bilan tasdiqlash

- API contract, xizmat ko‘rsatish huquqi va data processing agreement.
- Sandbox/service account, test yozuvlari, savollar/limitlar, idempotency & retry.
- Xatolarni kuzatish, audit trail, DLQ/rollback, oqimdagi sirlarni yashirish.
- Source of truth aniqligi: xodim, tarif, sinf, yil, qaror kimda asosiy ekanini belgilang.
