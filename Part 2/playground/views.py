from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, F, Count, Min, Max, Avg, Value, Func, ExpressionWrapper, DecimalField, Sum, CharField
from django.db.models.functions import Concat
from django.shortcuts import render

from store.models import Product, Customer, Collection, Order, OrderItem, Cart, CartItem

from tags.models import TaggedItem, Tag


def say_hello(request):
	queryset = Product.objects.filter()
	return render(request, 'hello.html', {'result': queryset})