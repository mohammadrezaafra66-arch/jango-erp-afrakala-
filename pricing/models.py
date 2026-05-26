from decimal import Decimal

from django.db import models

from catalog.models import Product
from core.models import TimeStampedModel


class ExchangeRate(TimeStampedModel):
    source = models.CharField(max_length=80, default="manual")
    currency = models.CharField(max_length=12, default="USD")
    rate_to_irr = models.DecimalField(max_digits=18, decimal_places=2)
    observed_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-observed_at"]

    def __str__(self) -> str:
        return f"{self.currency} {self.rate_to_irr}"


class PricingRule(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    profit_percent = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    freight_percent = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    extra_percent = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class ProductPrice(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="prices")
    buy_price = models.DecimalField(max_digits=18, decimal_places=2)
    sale_price = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=12, default="IRR")
    exchange_rate = models.ForeignKey(ExchangeRate, on_delete=models.SET_NULL, null=True, blank=True)
    rule = models.ForeignKey(PricingRule, on_delete=models.SET_NULL, null=True, blank=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["product", "is_current"])]

    def __str__(self) -> str:
        return f"{self.product.sku} - {self.sale_price}"


class PriceChangeLog(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_logs")
    old_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    new_price = models.DecimalField(max_digits=18, decimal_places=2)
    change_percent = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    reason = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.product.sku}: {self.old_price} -> {self.new_price}"
