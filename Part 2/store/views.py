from django.shortcuts import get_object_or_404

from django.db import transaction

from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from store.models import Product, Collection, Cart, CartItem, Customer, Order, OrderItem
from store.serializers import ProductSerializer, CollectionSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer, CustomerOrderSerializer, CreateOrderSerializer
from store.filters import ProductFilter
from store.pagination import DefaultPagination

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from .permissions import IsAdminUserOrReadOnly


class StoreProductViewSet(viewsets.ModelViewSet):
	queryset = Product.objects.select_related("collection").filter()[0:10]
	serializer_class = ProductSerializer
	lookup_field = 'product_id'

	def get_serializer_context(self):
		return {"request": self.request}

	def get_object(self):
		ID = self.kwargs.get("product_id")
		product = get_object_or_404(Product, id=ID)
		return product

	def destroy(self, request, pk=None):
		ID = self.kwargs.get("product_id")
		product = get_object_or_404(Product, id=ID)

		if product.order_products.count() > 0:
			return Response({"error": "Product cant be deleted"}, status=405)

		product.delete()
		return Response(status=204)


class StoreProductsList(ListCreateAPIView):
	queryset = Product.objects.filter()
	serializer_class = ProductSerializer
	filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
	# filterset_fields = ["collection_id", "unit_price"]
	filterset_class = ProductFilter
	search_fields = ["title", "description"]
	ordering_fields = ["unit_price", "last_update"]
	pagination_class = DefaultPagination
	permission_classes = [IsAdminUserOrReadOnly]


	def get_serializer_context(self):
		return {"request": self.request}


class StoreProductDetail(RetrieveUpdateDestroyAPIView):
	serializer_class = ProductSerializer
	permission_classes = [IsAdminUserOrReadOnly]

	def get_object(self):
		ID = self.kwargs.get("id")
		product = get_object_or_404(Product, id=ID)
		return product

	def delete(self, request, *args, **kwargs):
		ID = self.kwargs.get("id")
		product = get_object_or_404(Product, id=ID)

		if product.order_products.count() > 0:
			return Response({"error": "Product cant be deleted"}, status=405)

		product.delete()
		return Response(status=204)


class StoreCollectionViewSet(viewsets.ModelViewSet):
	queryset = Collection.objects.filter()
	serializer_class = CollectionSerializer
	lookup_field = "collection_id"

	def get_object(self):
		ID = self.kwargs.get("collection_id")
		collection = get_object_or_404(Collection, id=ID)
		return collection

	def destroy(self, request, pk=None):
		ID = self.kwargs.get("id")
		collection = get_object_or_404(Collection, id=ID)

		if collection.products.count() > 0:
			return Response({"error": "Collection cant be deleted"}, status=405)

		product.delete()
		return Response(status=204)


class StoreCollectionList(ListCreateAPIView):
	queryset = Collection.objects.filter()
	serializer_class = CollectionSerializer


class StoreCollectionDetail(RetrieveUpdateDestroyAPIView):
	serializer_class = CollectionSerializer

	def get_object(self):
		ID = self.kwargs.get("id")
		collection = get_object_or_404(Collection, id=ID)
		return collection

	def delete(self, request, *args, **kwargs):
		ID = self.kwargs.get("id")
		collection = get_object_or_404(Collection, id=ID)

		if collection.products.count() > 0:
			return Response({"error": "Collection cant be deleted"}, status=405)

		product.delete()
		return Response(status=204)


class CreateCart(CreateAPIView):
	serializer_class = CartSerializer


class CartDetail(RetrieveDestroyAPIView):
	serializer_class = CartSerializer

	def get_object(self):
		uid = self.kwargs.get('uid')

		return get_object_or_404(Cart, pk=uid)


class ItemView(ListCreateAPIView):
	def get_serializer_class(self):
		if self.request.method == 'POST':
			return AddCartItemSerializer
		return CartItemSerializer

	def get_queryset(self):
		string = self.kwargs.get("uid")
		return CartItem.objects.select_related('product').filter(cart_id=string)


class ItemDetailView(RetrieveUpdateDestroyAPIView):
	http_method_names = ['get', 'patch', 'delete']

	def get_serializer_class(self):
		if self.request.method == 'PATCH':
			return UpdateCartItemSerializer
		return CartItemSerializer

	def get_object(self):
		string = self.kwargs.get("id")

		return get_object_or_404(CartItem, pk=string)

class CustomerView(CreateAPIView):
	serializer_class = CustomerSerializer
	http_method_names = ["post"]
	permission_classes = [IsAuthenticated]


class CustomerDetail(RetrieveUpdateAPIView):
	serializer_class = CustomerSerializer
	http_method_names = ["post", 'get', 'patch']

	def get_permissions(self):
		if self.request.method == "GET":
			return [AllowAny()]
		return [IsAuthenticated()]

	def get_object(self):
		user = self.kwargs.get("id")
		print(self.request.user)
		return get_object_or_404(Customer, pk=user)

	# @action(detail=False, methods=["GET"])
	# def me(self, request):
	# 	customer, _ = Customer.objects.get_or_create(customer_id=request.user.id)

	# 	if request.method == 'GET':
	# 		serializer = CustomerSerializer(customer)
	# 		return Response(serializer.data)
	# 	elif request.method == 'POST':
	# 		serializer = CustomerSerializer(customer, data=request.data)
	# 		serializer.is_valid(raise_exception=True)
	# 		serializer.save()
	# 		return Response(serializer.data)


class CustomerOrders(ListCreateAPIView):
	permission_classes = [IsAuthenticated]

	@transaction.atomic()
	def get_queryset(self):
		if self.request.user.is_staff:
			return Order.objects.filter()
		
		customer = get_object_or_404(Customer, user_id=self.request.user.id)
		return Order.objects.filter(customer=customer)

	def get_serializer_context(self):
		return {"user_id": self.request.user.id}
	
	def get_serializer_class(self):
		if self.request.method == 'POST':
			return CreateOrderSerializer
		return CustomerOrderSerializer
