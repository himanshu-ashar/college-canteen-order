from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('',views.MultipleProducts, name='all'),
    path('details/<int:id>',views.SingleProduct,name='details'),
    #path('addCart/<int:id>',views.addToCart,name='addToCart'),
    # path('checkout/',views.CheckoutView.as_view(), name='checkout'),
    path('order-summary/',views.OrderSummaryView.as_view(), name='summary'),
    path('add-to-cart/<slug:slug>/',views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug:slug>/',views.remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug:slug>/',views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('checkout/',views.PlaceOrder.as_view(), name='checkout'),
    path('manage-orders/',views.OrderList.as_view(),name='manage-orders'),
    path('order-ready/<username>/<int:id>/',views.OrderReady.as_view(),name='order-ready'),
    path('order-cancelled/<username>/<int:id>/',views.OrderCancelled.as_view(),name='order-cancelled'),
    path('order-collected/<username>/<int:id>/',views.OrderCollected.as_view(),name='order-collected'),
]
