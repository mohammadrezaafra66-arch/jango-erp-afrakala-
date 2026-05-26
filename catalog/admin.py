from django.contrib import admin

from .models import Brand, Category, Product, Supplier


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "is_active", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "is_active", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "brand", "category", "supplier", "is_active", "updated_at")
    search_fields = ("sku", "name", "model_name")
    list_filter = ("brand", "category", "is_active")
