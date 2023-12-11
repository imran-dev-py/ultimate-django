from django.contrib import admin
from django.db.models import Count
from django.urls import reverse
from django.utils.html import format_html

from urllib.parse import urlencode

from store.models import (Product, Collection, Order, OrderItem, Cart, CartItem, Customer, OrderItem)

admin.site.register(OrderItem)

# custom filter 
class InventoryFilter(admin.SimpleListFilter):
	title = "Inventory"
	parameter_name = "inventory"

	less_than_10 = "<10"
	greater_than_50 = ">50"

	def lookups(self, request, model_admin):
		return [
			(self.less_than_10, "Low"),
			(self.greater_than_50, "Greater"),
		]

	def queryset(self, request, queryset):
		if self.value() == self.less_than_10:
			return queryset.filter(inventory__lt=10)

		if self.value() == self.greater_than_50:
			return queryset.filter(inventory__gt=50)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
	list_display = ["title", "products_count"]
	search_fields = ["title"]

	@admin.display(ordering="products_count")
	def products_count(self, collection):
		product_list_url  = reverse("admin:store_product_changelist")
		url_queries = urlencode({
			"collection_id": str(collection.id),
		})
		url_with_query_parameters = f"{product_list_url }?{url_queries}"

		return format_html("<a href='{}'>{}</a>", url_with_query_parameters, collection.products_count)

	def get_queryset(self, request):
		return super().get_queryset(request).annotate(products_count=Count("products"))


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	prepopulated_fields = {
		"slug": ["title"]
	}
	autocomplete_fields = ["collection"]
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
			return "Low"
		return "OK"

	@admin.action(description="Clear Inventory")
	def clear_inventory(self, request, queryset):
		updated_count = queryset.update(inventory=0)

		self.message_user(request, message=f"{updated_count} products were successfully updated.")


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
	list_display = ["first_name", "last_name", "membership", "orders"]
	list_editable = ["membership"]
	list_per_page = 10
	ordering = ["user__first_name", "user__last_name"]
	list_select_related = ["user"]
	autocomplete_fields = ["user"]
	search_fields = ["first_name__istartswith", "last_name__istartswith"]

	@admin.display(ordering="orders_count")
	def orders(self, customer):
	    product_list_url = reverse("admin:store_order_changelist")
	    url_queries = urlencode({"customer_id": str(customer.id)})
	    url_with_query_parameters = f"{product_list_url}?{url_queries}"
	    
	    return format_html("<a href='{}'>{} orders</a>", url_with_query_parameters, customer.orders_count)
	  
	def get_queryset(self, request):
	    return super().get_queryset(request).annotate(orders_count=Count("orders"))


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ["product"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer"]
    list_select_related = ["customer"]
    autocomplete_fields = ["customer"]
    inlines = [OrderItemAdmin]


admin.site.register(Cart)
admin.site.register(CartItem)