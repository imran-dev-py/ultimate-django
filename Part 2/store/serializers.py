from decimal import Decimal

from rest_framework import serializers

from store.models import Collection, Product, Cart, CartItem, Customer, Order, OrderItem

from django.core.validators import MinValueValidator

from core.serializers import UserCreateSerializer

from django.shortcuts import get_object_or_404

from django.db import transaction


class CollectionSerializer(serializers.Serializer):
	id = serializers.IntegerField(required=False)
	title = serializers.CharField(max_length=200)
	products_count = serializers.SerializerMethodField()

	def get_products_count(self, collection):
		return collection.products.count()

	def create(self, validated_data):
		return Collection.objects.create(**validated_data)

	def update(self, instance, validated_data):
		instance.title = validated_data.get("title")
		instance.save()
		return instance


class ProductSerializer(serializers.Serializer):
	id = serializers.IntegerField(required=False)
	title = serializers.CharField(max_length=200)
	price = serializers.DecimalField(max_digits=6, decimal_places=2, source="unit_price")
	price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
	collection = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.filter(), pk_field=id)
	# collection = serializers.StringRelatedField(read_only=True)
	# collection = serializers.HyperlinkedRelatedField(queryset=Collection.objects.filter(), view_name="collection-detail", lookup_field='id')
	# collection = CollectionSerializer(read_only=True)
	inventory = serializers.IntegerField()
	description = serializers.CharField(max_length=500)
	
	def calculate_tax(self, product):
		return round(product.unit_price * Decimal(1.1), 3)

	def create(self, validated_data):
		return Product.objects.create(**validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
	class Meta:
		model = Product 
		fields = ["id", "title", 'unit_price']
		read_only_fields = fields


class CartItemSerializer(serializers.ModelSerializer):
	product = SimpleProductSerializer(read_only=True)

	total_price = serializers.SerializerMethodField(method_name='calculatePrice')

	def calculatePrice(self, cart_item):
		return cart_item.product.unit_price * cart_item.quantity

	class Meta:
		model = CartItem  
		fields = ["id", "product", "quantity", "total_price"]
		read_only_fields = fields


class CartSerializer(serializers.ModelSerializer):

	cart_items = CartItemSerializer(many=True, read_only=True)
	total_price = serializers.SerializerMethodField()

	# def get_total_price(self, cart):
	# 	return sum([item.total_price for item in cart.cart_items.all()])
	
	def get_total_price(self, cart):
		total_price = []
		for item in cart.cart_items.all():
			total_price.append(item.product.unit_price * item.quantity)

		return sum(total_price)

	class Meta:
		model = Cart 
		fields = ["id", "created_at", "cart_items", "total_price"]
		read_only_fields = fields

	def create(self, validated_data):
		return Cart.objects.create(**validated_data)


class AddCartItemSerializer(serializers.ModelSerializer):
	product_id = serializers.IntegerField()
	quantity = serializers.IntegerField(validators=[MinValueValidator(1)])

	class Meta:
		model = CartItem  
		fields = ["id", "product_id", "quantity"]
		read_only_fields = ["id"]

	

	def save(self, **kwargs):
		cart_id = self.context["view"].kwargs.get("uid")
		product_id = self.validated_data['product_id']
		quantity = self.validated_data.get("quantity")

		try:
			cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
			cart_item.quantity += quantity
			cart_item.save()
			self.instance = cart_item
		except CartItem.DoesNotExist:
			self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

		return self.instance


	def validate_product_id(self, value):
		if not Product.objects.filter(pk=value).exists():
			raise serializers.ValidationError({"detail": "Product doesn't exist with this id"})
		return value


class UpdateCartItemSerializer(serializers.ModelSerializer):
	class Meta:
		model = CartItem
		fields = ["quantity"]
		read_only_fields = ["id"]


class CustomerSerializer(serializers.ModelSerializer):
	user_id = serializers.IntegerField()

	class Meta:
		model = Customer 
		fields = ["id", "user_id", "birth_date", "membership", "phone"]
		read_only_fields = ["id"]

	def create(self, validated_data):
		return Customer.objects.create(
			birth_date=self.validated_data["birth_date"], membership = self.validated_data["membership"], phone=self.validated_data["phone"], user_id=self.validated_data["user_id"]
		)


class OrderIteSerializer(serializers.ModelSerializer):
	product = SimpleProductSerializer(read_only=True)
	
	class Meta:
		model = OrderItem
		fields = ["id", "product", "quantity", "unit_price"]
		


class CustomerOrderSerializer(serializers.ModelSerializer):
	customer = CustomerSerializer(read_only=True)
	order_items = OrderIteSerializer(many=True)

	class Meta:
		model = Order 
		fields = ["id", "customer","payment_status", "order_items"]
		read_only_fields = fields


class CreateOrderSerializer(serializers.Serializer):
	cart_id = serializers.UUIDField()

	def save(self, **kwargs):
		user_id = self.context["user_id"]
		cart_id = self.validated_data.get("cart_id")

		customer = get_object_or_404(Customer, user_id=user_id)
		order = Order.objects.create(customer=customer)
		print(order, '**********')
		return order