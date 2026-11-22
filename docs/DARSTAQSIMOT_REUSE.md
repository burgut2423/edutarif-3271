# `burgut2423/darstaqsimot` → `burgut2423/edutarif-3271`: selektiv integratsiya

**Tekshirildi:** 2026-11-23; manba: https://github.com/burgut2423/darstaqsimot (`main`, tekshirilgan commit `c84983ecff3af0f90e3494050791a266b611d3b6`).

**Maqsad:** manba React/TypeScript prototipidagi yaxshi UX/mantiq g‘oyalarini serverda qat'iy rollar, tenant (maktab), o‘quv yili va audit talablariga moslashtirish. **Bir butun loyihani ko‘chirish / import qilinadigan autentifikatsiya va 3271/823 qaror mexanizmini olish xavfli.**

## Sinab ko‘rilgan modullar

| Manbadagi fayl | Yutuq | Qaror |
|---|---|---|
| `src/components/modules/ClassesModule.tsx` | Bir daraja uchun 1–10 parallel sinfni yaratish, allaqachon mavjudlarni tashlab ketish | **Port qilindi**: `POST /school/classes/batch`, sinflar loyiha holatida va faqat maktab admini uchun |
| `src/components/modules/CurriculumModule.tsx` | 1–11-sinf × fan ustunli o‘quv soati matritsasi va yig‘indilar | **Port qilindi**: `GET /school/matrix`, Jinja + DB, faol o‘quv yili, sinf/fan/guruh hisobi |
| `src/components/modules/DistributionModule.tsx` | Taqsimlangan/bo‘sh soat, fan va sinf tahlili | **Port qilindi**: `app/curriculum_matrix.py` faqat o‘qish, loyihaviy/tasdiqlangan soat alohida, CSV |
| `src/utils/distributionEngine.ts` | Taqsimot loyihasi uchun evristika | **Ko‘chirilmagan**: fan malakasi bo‘lmaganda boshqa pedagoglarga fallback, 30 soatga qadar majburiy to‘ldirish, guruhlarga avtomatik bo‘lish va umumiy ballga qarab ustuvorlik manbai rasmiy talablarga mosligi tasdiqlanmagan |
| `src/components/modules/Ustama823Module.tsx` | Baholash ekranining UI g‘oyalari | **Hali ko‘chirilmagan**: qat’iy, versiyalangan 823-ilovalar va ishchi guruh ruxsatlari bilan tekshirish kerak |
| `src/utils/excelExporter.ts` | Excel ko‘rinishidagi eksport | **Qisman moslashtirilgan**: mustaqil CSV eksport, formulani xavfsizlashtirish; to‘liq XLSX keyingi bosqich |
| `src/components/modules/VacanciesModule.tsx`, `WaivedHoursModule.tsx`, `TeachersModule.tsx`, `ReportsModule.tsx` | Hisobotlar va maktab ichidagi qo‘shimcha jarayonlar | **Keyingi bosqichga qoldirildi**: yangi ma'lumotlar modeli, ruxsatlar, hujjatlar va audit sxemasi zarur |
| `src/App.tsx`, `src/components/LoginModal.tsx`, `src/data/initialData.ts` | SPA lokal holat/demo login/namuna ma'lumot | **Ko‘chirilmagan**: autentifikatsiya/serverga tayangan real tizimga to‘g‘ri kelmaydi |

## Bu commitdagi xavfsiz amaliy integratsiya

1. `app/controllers/school.py`: `/classes/batch` POST. Maktab ID faqat autentifikatsiyadan keladi, faol yil ishlatiladi, CSRF va rol nazorati bor, 1–11-sinf/1–10 parallel/1–60 o‘quvchi/til tekshiriladi, dublikatlar yaratmaydi, audit yozadi.
2. `app/controllers/matrix.py`: `/school/matrix`, `/school/matrix/export.csv`; faqat shu maktab va faol o‘quv yilining read-only ma'lumotlari.
3. `app/curriculum_matrix.py`: sinf × fan pivot hisoboti; o‘quv soatini guruhlar bilan ko‘paytiriladigan pedagogik soatdan ajratadi; `superseded` yozuvlar hisobga olinmaydi.
4. `app/templates/matrix.html`, `app/templates/classes.html`, `app/templates/base.html`, `app/static/style.css`: mobilga mos maktab paneli va bulk yaratish formasi.
5. `tests/test_reused_darstaqsimot.py`: school/year isolation, grade filter, draft creation, 2 guruh summasi, tarix yozuvlarini chiqarib tashlash, role/CSRF va CSV formuladan himoya testlari.

## Keyin qilish kerak

- Rasmiy 2026/2027 o‘quv reja variantlari bilan fan-by-grade matrisa solishtirish; tasdiqlangan normativ manba bilan qat'iy moslik.
- Bo‘linadigan sinflarda guruhlar sonini hukumat me'yoriga muvofiq tekshirish (avtomatik 2-guruh tayinlamaslik).
- Mavjud 3271 taqsimot tavsiyasini bir nechta sinf bo‘ylab *jami* yuklama va ustuvorliklar bilan izchil hisoblaydigan, tushuntiriladigan **faqat loyiha** engine; tasdiq vakolatli insonda qoladi.
- 823 kalkulyatorini to‘liq rasmiy ilovalar, mezon dalillari va ishchi guruh tasdiqlash bosqichlari bilan tekshirib integratsiya qilish.
- Excel XLSX export, xodim importi, vakansiyalar, soatdan voz kechish va rayon kesimidagi analitika modullarini hujjatlashtirib rivojlantirish.

**Eslatma:** Manba repository jamoa mulki bo‘lsa ham, har bir kelgusidagi koddan foydalanishda mualliflik/licenziya holatini tekshirib, manbani qayd qilish kerak. Ushbu integratsiyada kod satrma-satr ko‘chirilmadi, balki mos funksiyalar Python/Jinja server modeli uchun qayta yozildi.
