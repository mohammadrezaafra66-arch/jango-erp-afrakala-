from django.contrib import admin

from .models import ExchangeRate, PriceChangeLog, PricingRule, ProductPrice


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("currency", "rate_to_irr", "source", "observed_at", "is_active")
    list_filter = ("currency", "source", "is_active")


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "profit_percent", "freight_percent", "extra_percent", "is_active")
    list_filter = ("is_active",)


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ("product", "buy_price", "sale_price", "currency", "is_current", "created_at")
    list_filter = ("currency", "is_current")
    search_fields = ("product__sku", "product__name")


@admin.register(PriceChangeLog)
class PriceChangeLogAdmin(admin.ModelAdmin):
    list_display = ("product", "old_price", "new_price", "change_percent", "created_at")
    search_fields = ("product__sku", "product__name", "reason")
