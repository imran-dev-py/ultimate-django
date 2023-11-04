from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, F, Count, Min, Max, Avg, Value, Func, ExpressionWrapper, DecimalField, Sum, CharField
from django.db.models.functions import Concat
from django.shortcuts import render

from django.contrib.auth.models import User



from store.models import Product, Customer, Collection, Order, OrderItem, Cart, CartItem

from tags.models import TaggedItem, Tag


def say_hello(request):
	# queryset = Collection.objects.aggregate(count=Count("title"), max_price=Avg("product__unit_price"))
	# queryset = Collection.objects.annotate(new_id=F("id")+1).order_by("-id")
	# queryset = User.objects.annotate(
	# 	full_name = Func(F("first_name"), Value(" "), F("last_name"), function='CONCAT')
	# )
	# queryset = User.objects.annotate(full_name=Concat(F("first_name"), Value(" "), F("last_name")))
	# queryset = Customer.objects.annotate(orders_count=Count("order"))

	# discounted_price = ExpressionWrapper(F("unit_price") * 0.8, output_field=DecimalField())
	# queryset = Product.objects.annotate(discounted_price=discounted_price)

	# queryset = TaggedItem.objects.get_for_tags(Product, 1)
	# queryset = TaggedItem.objects.get(tag_id=1)

	# Creating object
	# tag = Tag()
	# tag.label = "react"
	# tag.save()

	# Update object
	queryset=Tag.objects.filter(label="react").update(label="Reactjs")
	queryset = TaggedItem.objects.raw('SELECT * FROM tag_taggeditem')

	# Delete object
	#Tag.objects.filter(label="Tailwind CSS").delete()


	print(queryset)

	return render(request, 'hello.html', {'name': 'Raphael', 'result': queryset})