# AI Help — Telegram yordam boti

User botga yozadi → adminga karta keladi → admin **✍️ Javob yozish** tugmasini
bosadi yoki kartaga **Reply** qiladi → javob userga uning savoliga reply bo'lib boradi.

- Ro'yxatdan o'tish: til (uz/ru/en) + telefon (ixtiyoriy)
- Har qanday turdagi xabar: matn, rasm, albom, video, ovoz, fayl, GIF, lokatsiya
- Bitta javob userning barcha ochiq murojaatlarini yopadi, kartalar hamma adminlarda yangilanadi
- Ilova: `/start` dagi **📲 Ilovani yuklab olish** tugmasi yoki menyudagi `/yuklash` — userga
  APK yuboriladi (faqat Android). Menyu izohlari user tanlagan tilda.
  - **APK qo'yish / yangilash:** admin `.apk` faylni botga oddiy Telegram orqali tashlaydi
    (kartaga Reply qilmasdan). Bot `file_id` ni `data/apk.json` ga saqlaydi va userlarga shuni
    yuboradi — fayl Telegram serverida turadi, hajm cheklovi yo'q (100 MB+ ham bo'ladi).
    Tekshirish: adminning o'zi `/yuklash` bosadi.

## Serverga o'rnatish (Linux, systemd)

Python 3.10+ kerak.

1. Kod va virtual muhit:
   ```bash
   sudo mkdir -p /opt/aihelp && sudo chown $USER /opt/aihelp
   git clone -b server <repo-url> /opt/aihelp
   cd /opt/aihelp
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   ```
2. `/opt/aihelp/.env`:
   ```
   BOT_TOKEN=<BotFather tokeni>
   ADMIN_IDS=111111111,222222222
   DJANGO_SECRET_KEY=<uzun tasodifiy qator>

   # Server Telegram'ga faqat proxy orqali chiqsa:
   # TELEGRAM_PROXY=http://<proxy>:<port>
   ```
   Tasodifiy kalit: `venv/bin/python -c "import secrets; print(secrets.token_urlsafe(50))"`
3. Noutbukdagi ma'lumotlarni ko'chirish (userlar, yozishmalar, APK): noutbukdagi
   `data\db.sqlite3` va `data\apk.json` → serverdagi `/opt/aihelp/data/`.
   **Avval noutbukdagi botni to'xtating** — bitta token bilan ikki bot ishlay olmaydi (409).
4. Baza:
   ```bash
   venv/bin/python manage.py migrate
   ```
5. Xizmatlar (`deploy/*.service` ichidagi `User=` ni o'zingizning foydalanuvchiga moslang):
   ```bash
   sudo cp deploy/aihelp-bot.service deploy/aihelp-panel.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now aihelp-bot aihelp-panel
   ```

Boshqarish:
```bash
sudo systemctl status aihelp-bot            # holat
sudo journalctl -u aihelp-bot -f            # loglar
sudo systemctl restart aihelp-bot           # kod yangilangandan keyin
```

Yangilash: `git pull && venv/bin/pip install -r requirements.txt && sudo systemctl restart aihelp-bot aihelp-panel`.

Botning admin paneli faqat serverning o'ziga ochiq (`127.0.0.1:8010`). Ko'rish:
`ssh -L 8010:127.0.0.1:8010 <server>` → http://localhost:8010/admin/.
Superuser: `venv/bin/python manage.py createsuperuser`.
