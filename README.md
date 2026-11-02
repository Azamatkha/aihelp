# AI Help — Telegram yordam boti

User botga yozadi → adminga karta keladi → admin **✍️ Javob yozish** tugmasini
bosadi yoki kartaga **Reply** qiladi → javob userga uning savoliga reply bo'lib boradi.

- Ro'yxatdan o'tish: til (uz/ru/en) + telefon (ixtiyoriy)
- Har qanday turdagi xabar: matn, rasm, albom, video, ovoz, fayl, GIF, lokatsiya
- Bitta javob userning barcha ochiq murojaatlarini yopadi, kartalar hamma adminlarda yangilanadi
- Admin panel: `/admin/` — userlar, yozishmalar, filtrlar, qidiruv

## O'rnatish (Windows)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # ichini to'ldiring
python manage.py migrate
python manage.py createsuperuser
```

## Ishga tushirish

```powershell
python manage.py runbot                                            # bot
python -m waitress --listen=127.0.0.1:8000 config.wsgi:application # panel
```

Avtomatik ishga tushish (Administrator PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install_autostart.ps1
```

Loglar: `logs\bot.log`, `logs\panel.log`.

## Docker

```bash
docker compose up -d --build
```