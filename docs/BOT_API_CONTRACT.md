# Bot API Contract — AfraKala Django ERP

## اصل ارتباط ربات‌ها

ربات‌ها نباید مستقیم به دیتابیس ERP وصل شوند. ارتباط باید از طریق API محدود، مستند، لاگ‌دار و دارای کلید انجام شود.

## قرارداد فعلی شناخته‌شده از پروژه قبلی

endpoint درست برای خواندن کالاها در وب‌اپ قبلی:

```http
GET /api/public/bot/products?page=1&page_size=2
Header: bot api key header
```

رفتارهای مورد انتظار:

- نبودن کلید یا کلید نامعتبر: `401` با JSON
- کلید غیرفعال: `403` با JSON
- کلید معتبر: `200`
- service role و secret فقط server-side

## قرارداد پیشنهادی برای Django

### Products list

```http
GET /api/public/bot/products/?page=1&page_size=50
Header: bot api key header
```

### Response 200

```json
{
  "count": 120,
  "page": 1,
  "page_size": 50,
  "results": [
    {
      "id": "uuid",
      "sku": "TV-SAMSUNG-55-001",
      "name": "تلویزیون سامسونگ ۵۵ اینچ",
      "brand": "Samsung",
      "category": "TV",
      "is_active": true,
      "latest_price": {
        "amount": 45000000,
        "currency": "IRR",
        "changed_at": "2026-05-26T00:00:00Z"
      }
    }
  ]
}
```

## امنیت

- API key باید hash شده ذخیره شود.
- کلید خام نباید در دیتابیس یا لاگ ذخیره شود.
- هر درخواست باید audit شود.
- scope کلیدها باید محدود باشد؛ مثلاً `products:read` یا `prices:write`.
- rate limit در فاز بعد اضافه شود.

## خطای ساختاری در پروژه قبلی

در پروژه قبلی مسیر direct table access برای bot api keys مسیر اشتباه بود. مسیر درست، route عمومی کنترل‌شده در لایه server بود.

## نکته فنی قبلی

در پروژه قبلی، خطای 500 مربوط به init شدن Supabase admin client در Node 20 بدون native WebSocket support بود. در Django این مشکل عیناً وجود ندارد، اما اصل جداسازی secret و client server-side باید حفظ شود.
