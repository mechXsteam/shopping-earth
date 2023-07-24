from rest_framework.routers import SimpleRouter

from .views import ProductViewSet, CreateOrderViewSet, CreateOrderItemViewSet, ReviewProductViewSet

router = SimpleRouter()

# the order kind of works this way, changing the order may cause some issues.
router.register('review', ReviewProductViewSet)
router.register('order', CreateOrderViewSet, basename='order')
router.register('orderitem', CreateOrderItemViewSet)
router.register('', ProductViewSet, basename='product')

urlpatterns = router.urls
