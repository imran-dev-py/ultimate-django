from django.urls import path

from playground.views import say_hello

urlpatterns = [
	path("/hello", say_hello),
]