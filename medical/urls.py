from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('items', views.ItemViewSet, basename='items')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('patients', views.PatientViewSet)
router.register('orders', views.OrderViewSet, basename='orders')
router.register('reports', views.ReportViewSet, basename='reports')
router.register('feedbacks', views.FeedbackViewSet, basename='feedbacks')

items_router = routers.NestedDefaultRouter(
    router, 'items', lookup='item')
items_router.register('reviews', views.ReviewViewSet,
                         basename='item-reviews')
items_router.register(
    'images', views.ItemImageViewSet, basename='item-images')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

# URLConf
urlpatterns = router.urls + items_router.urls + carts_router.urls
