from django.urls import path, include

from rest_framework.routers import SimpleRouter, DefaultRouter

from store import views

# router = DefaultRouter()
# router.register('/products', views.StoreProductViewSet, basename="products")
# router.register("/collections", views.StoreCollectionViewSet, basename="collections")



urlpatterns = [
	path("api-auth/", include("rest_framework.urls")),
	path("/products", views.StoreProductsList.as_view(), name="products-list"),
	path("/products/<int:id>", views.StoreProductDetail.as_view(), name="product-detail"),
	path("/collections", views.StoreCollectionList.as_view(), name="collections"),
	path("/collections/<int:id>", views.StoreCollectionDetail.as_view(), name="collection-detail"),
	path("/carts/<uuid:uid>/items/<int:id>", views.ItemDetailView.as_view()),
	path("/carts/<uuid:uid>/items", views.ItemView.as_view()),
	path("/carts/<uuid:uid>", views.CartDetail.as_view(), name="cart-detail"),
	path("/carts", views.CreateCart.as_view(), name="cart"),
	path("/customers", views.CustomerView.as_view(), name="customer"),
	path("/customers/<int:id>", views.CustomerDetail.as_view(), name="customer-detail"),
	path("/orders", views.CustomerOrders.as_view(), name="customer-orders"),
]