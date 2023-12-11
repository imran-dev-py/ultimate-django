from django.core.validators import MinValueValidator
from django.db import models

import uuid

from core.models import User
from django.contrib import admin

class Promotion(models.Model):
	description = models.CharField(max_length=500)
	discount = models.FloatField()

	def __str__(self):
		return f"Discount is {self.discount}"

	class Meta:
		verbose_name = "Promotion"
		verbose_name_plural = "Promotions"


class Collection(models.Model):
	title = models.CharField(max_length=200)
	featured_product = models.ForeignKey(
		to="Product",
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="+"
	)

	def __str__(self):
		return f"{self.title}"

	class Meta:
		verbose_name = "Collection"
		verbose_name_plural = "Collections"
		ordering = ["-title"]


class Product(models.Model):
	title = models.CharField(max_length=150)
	slug = models.SlugField()
	description = models.TextField(null=True, blank=True)
	unit_price = models.DecimalField(
		max_digits=6,
		decimal_places=2,
		validators=[MinValueValidator(1)]
	)
	inventory = models.IntegerField(validators=[MinValueValidator(1)])
	last_update = models.DateTimeField(auto_now=True)
	collection = models.ForeignKey(
		to="Collection",
		on_delete=models.PROTECT,
		related_name="products"
	)
	promotions = models.ManyToManyField(
		to=Promotion,
		blank=True,
		related_name="product_promotions"
	)

	def __str__(self):
		return f"{self.title} is in {self.collection}"

	class Meta:
		verbose_name = "Product"
		verbose_name_plural = "Products"
		ordering = ["-title"]


class Customer(models.Model):
	MEMBERSHIP_BRONZE = "B"
	MEMBERSHIP_SILVER = "S"
	MEMBERSHIP_GOLD = "G"

	MEMBERSHIP_CHOICES = [
		(MEMBERSHIP_BRONZE, "B"),
		(MEMBERSHIP_SILVER, "S"),
		(MEMBERSHIP_GOLD, "G")
	]

	
	phone = models.CharField(max_length=15)
	birth_date = models.DateField(null=True)
	membership = models.CharField(
		max_length=1,
		choices=MEMBERSHIP_CHOICES,
		default=MEMBERSHIP_BRONZE
	)
	user = models.OneToOneField(to=User, on_delete=models.CASCADE, related_name="customer_users")

	def __str__(self):
		return f"{self.user.first_name} {self.user.last_name}"

	@admin.display(ordering="user__first_name")
	def first_name(self):
		return self.user.first_name

	@admin.display(ordering="user__first_name")
	def last_name(self):
		return self.user.last_name

	class Meta:
		verbose_name = "Customer"
		verbose_name_plural = "Customers"
		ordering = ["user__first_name", "user__last_name"]


class Order(models.Model):
	PAYMENT_STATUS_PENDING = "P"
	PAYMENT_STATUS_COMPLETE = "C"
	PAYMENT_STATUS_FAILED = "F"

	PAYMENT_STATUS_CHOICES = [
	    (PAYMENT_STATUS_PENDING, "Pending"),
	    (PAYMENT_STATUS_COMPLETE, "Complete"),
	    (PAYMENT_STATUS_FAILED, "Failed"),
	]

	placed_at = models.DateTimeField(auto_now_add=True)
	payment_status = models.CharField(
	    max_length=1,
	    choices=PAYMENT_STATUS_CHOICES,
	    default=PAYMENT_STATUS_PENDING
	)
	customer = models.ForeignKey(
		to=Customer,
		on_delete=models.PROTECT,
		related_name="orders"
	)

	def __str__(self):
		orderitems = self.order_items.filter()
		order_products = []

		for order_product in orderitems:
			order_products.append(order_product.product.title)

		return f"{order_products} is ordered by {self.customer.user.first_name}"

	class Meta:
		verbose_name = "Order"
		verbose_name_plural = "Orders"
		permissions = [
			("cancel_order", "Can cancel order")
		]


class OrderItem(models.Model):
	order = models.ForeignKey(
		to=Order,
		on_delete=models.PROTECT,
		related_name="order_items"
	)
	product = models.ForeignKey(
		to=Product,
		on_delete=models.PROTECT,
		related_name="order_products"
	)
	quantity = models.PositiveSmallIntegerField()
	unit_price = models.DecimalField(max_digits=6, decimal_places=2)

	def __str__(self):
		return f"{self.product.title}"

	class Meta:
		verbose_name = "OrderItem"
		verbose_name_plural = "OrderItems"


class Address(models.Model):
	street = models.CharField(max_length=255)
	city = models.CharField(max_length=255)
	customer = models.ForeignKey(
		to=Customer,
		on_delete=models.CASCADE,
		related_name="addresses"
	)

	def __str__(self):
		return f"{self.customer.first_name}"

	class Meta:
		verbose_name = "Address"
		verbose_name_plural = "Addresses"


class Cart(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.id}"

	class Meta:
		verbose_name = "Cart"
		verbose_name_plural = "Carts"


class CartItem(models.Model):
	cart = models.ForeignKey(
		to=Cart,
		on_delete=models.CASCADE,
		related_name="cart_items"
	)
	product = models.ForeignKey(
		to=Product,
		on_delete=models.CASCADE,
		related_name="cart_products"
	)
	quantity = models.PositiveSmallIntegerField()

	def __str__(self):
		return f"{self.product.title}"

	class Meta:
		verbose_name = "CartItem"
		verbose_name_plural = "CartItems"
		unique_together = [["cart", "product"]]