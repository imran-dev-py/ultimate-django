from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from urllib.parse import urlencode
from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = "Inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [
            ("<10", "LOW"),
            (">50", "Boom"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)

        if self.value() == ">50":
            return queryset.filter(inventory__gt=50)


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]
    search_fields = ["title"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        x = reverse("admin:store_product_changelist")
        y = urlencode({"collection_id": str(collection.id)})
        url = f"{x}?{y}"

        return format_html("<a href='{}'>{}</a>", url, collection.products_count)

    def get_queryset(self, request):
        # return models.Collection.objects.annotate(products_count=Count("product"))
        return super().get_queryset(request).annotate(products_count=Count("product"))


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["title"]}
    autocomplete_fields = ["collection"]
    # fields = ["title", "slug", "unit_price"]
    actions = ["clear_inventory"]
    list_display = ["title", "unit_price", "inventory_status", "collection_title"]
    list_editable = ["unit_price"]
    list_per_page = 10
    list_select_related = ["collection"]
    list_filter = ["collection", "last_update", InventoryFilter]
    search_fields = ["title"]

    @admin.display(ordering="collection_title")
    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering="inventory")
    def inventory_status(self, product):
        if product.inventory < 10:
            return "LOW"
        return "OK"

    @admin.action(description="Clear Inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)

        self.message_user(
            request, f"{updated_count} products were successfully updated."
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders"]
    list_editable = ["membership"]
    list_per_page = 10
    ordering = ["first_name", "last_name"]
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="orders_count")
    def orders(self, customer):
        x = reverse("admin:store_order_changelist")
        y = urlencode({"customer_id": str(customer.id)})
        url = f"{x}?{y}"
        html = format_html("<a href='{}'>{} orders</a>", url, customer.orders_count)
        return html

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count("order"))


class OrderItemAdmin(admin.TabularInline):
    model = models.OrderItem
    extra = 1
    autocomplete_fields = ["product"]


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer"]
    list_select_related = ["customer"]
    autocomplete_fields = ["customer"]
    inlines = [OrderItemAdmin]
