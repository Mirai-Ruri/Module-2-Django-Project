"""
URL configuration for crystal_django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    # Admin Dashboard
    path("update/user/role/<int:id>/", views.update_user_role),
    path("work/place/", views.product_list),
    path("registered/users/", views.registered_users),
    path("order/list/add/<int:id>/", views.order_add),
    path("order/list/view/", views.order_view),
    path("user/message/", views.user_message),
    path("user/message/delete/<int:pk>/", views.user_message_delete),
    path("user/message/list/", views.user_message_list),
    path("user/message/detail", views.user_message_detail),
    # Login, Logout, Register, Delete, Password
    path("", views.index),
    path("user/logout/", views.user_logout),
    path("user/register/", views.user_register),
    path("user/update/<int:pk>/", views.user_update),
    path("user/delete/<int:pk>/", views.user_delete),
    path("change/password/",views.change_password),
    # Main
    path("main/page/", views.main),
    # Wishlist
    path("wish/list/add/<int:id>/", views.wishlist_add),
    path("wish/list/delete/<int:id>/", views.wishlist_delete),
    path("wish/list/view/", views.wishlist_view),
    # Cart
    path("cart/list/add/<int:id>/",views.cart_add),
    path("cart/list/delete/<int:id>/",views.cart_delete),
    path("cart/list/view/",views.cart_view),
    # Contact
    path("contact/", views.contact),
    # Product
    path("product/create/", views.product_create),
    path("product/update/<int:pk>/", views.product_update),
    path("product/delete/<int:pk>/", views.product_delete),
    path("product/detail/<int:pk>/", views.product_detail),
    # Category
    path("category/create/", views.category_create),
    path("category/delete/<int:pk>/", views.category_delete),
    path("category/list/", views.category_list),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
