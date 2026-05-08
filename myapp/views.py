from django.shortcuts import render, redirect, get_object_or_404
from myapp.models import (
    TimeStampedModel,
    ProfileModel,
    ProductModel,
    CategoryModel,
    OrderListModel,
    CartListModel,
    WishListModel,
    MessageModel,
)
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import permission_required

# Create your views here.

# ==========ADMIN DASHBOARD==========


# def is_admin(user):
#     return user.is_superuser


# @user_passes_test(is_admin)
@login_required(login_url="/")
def update_user_role(request, id):
    if not request.user.is_superuser:
        return redirect("/main/page/")
    if request.method == "POST":
        user = User.objects.get(id=id)
        user.is_superuser = "is_superuser" in request.POST
        user.is_staff = "is_staff" in request.POST
        user.is_active = "is_active" in request.POST
        user.save()
        messages.success(request, f"Account for {user.username} Updated.")
    return redirect("/registered/users/")


@login_required(login_url="/")
# @permission_required('auth.change_user', raise_exception=True)
def registered_users(request):
    if not request.user.is_staff:
        return redirect("/main/page/")
    search = request.GET.get("search")
    # users = User.objects.all().order_by("-date_joined")
    users = User.objects.select_related("profilemodel").all().order_by("-date_joined")

    if search:
        users = users.filter(
            Q(username__icontains=search) | Q(email__icontains=search)
        ).order_by("-date_joined")

    context = {
        "user_count": User.objects.count(),
        "users": users,
    }

    return render(request, "registered_users.html", context)


@login_required(login_url="/")
def user_message(request):
    if request.method == "POST":
        user_message = request.POST.get("message")
        user_message = MessageModel.objects.create(
            user_message=user_message, author=request.user
        )
        user_message.save()
        messages.info(request, "Message Sent.")
        return redirect("/contact/")


@login_required(login_url="/")
def user_message_delete(request, pk):
    if not request.user.is_staff:
        return redirect("/main/page/")
    user_message = MessageModel.objects.get(id=pk)
    if request.method == "POST":
        user_message.delete()
        messages.error(request, "Message Deleted.")
        return redirect("/user/message/list/")


@login_required(login_url="/")
def user_message_list(request):
    if not request.user.is_staff:
        return redirect("/main/page/")
    search = request.GET.get("search")
    user_messages = MessageModel.objects.all()

    if search:
        user_messages = user_messages.filter(
            Q(author__username__icontains=search) | Q(author__email__icontains=search)
        ).order_by("-created_at")
    context = {
        "message_count": MessageModel.objects.count(),
        "user_messages": user_messages,
    }

    return render(request, "message.html", context)


@login_required(login_url="/")
def user_message_detail(request, pk):
    if not request.user.is_staff:
        return redirect("/main/page/")
    user_message = MessageModel.objects.get(id=pk)
    return render(request, "message.html", {"user_message": user_message})


# ==========LOGIN/LOGOUT/REGISTER/CHANGE_PASSWORD==========


def index(request):
    if request.method == "GET":
        return render(request, "index.html")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(
            username=username,
            password=password,
        )
        if user:
            login(request, user)
            messages.success(request, "You have logged in successfully.")
            return redirect("/main/page/")
        else:
            messages.warning(request, "Sorry. Login failed.")
            return redirect("/")


def user_logout(request):
    logout(request)
    messages.warning(request, "You have logged out. Come back.")
    return redirect("/")


def user_register(request):
    if request.method == "GET":
        return render(request, "register.html")
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        image = request.FILES.get("image")
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        if image:
            ProfileModel.objects.create(user=user, image=image)
        else:
            ProfileModel.objects.create(user=user)

        # ProfileModel.objects.create(user=user, image=image)

        messages.success(request, "You have registered successfully. Please log in.")
        return redirect("/")


@login_required(login_url="/")
def user_update(request, pk):
    user = User.objects.get(id=pk)

    if request.method == "GET":
        return render(request, "index.html", {"user": user})
    if request.method == "POST":
        username = request.POST.get("username")
        image = request.FILES.get("image")
        user.username = username
        if image:
            user.profilemodel.image.delete()
            user.profilemodel.image = image
            user.profilemodel.save()
        user.save()
        messages.info(request, "Profile Updated.")
        return redirect("/main/page/")


def user_delete(request, pk):
    user = User.objects.get(id=pk)
    if request.method == "GET":
        return render(request, "registered_users.html", {"user": user})
    if request.method == "POST":
        if user.profilemodel.image != "user_profile_images/default_profile.png":
            user.profilemodel.image.delete()
        user.delete()
        if request.user.is_superuser:
            messages.error(request, "You have deleted this account.")
        else:
            messages.error(request, "You have deleted you account.")
            logout(request)
        return redirect("/registered/users/")


def change_password(request):
    if request.method == "GET":
        return render(request, "main.html")
    if request.method == "POST":
        old_pw = request.POST.get("old_pw")
        new_pw = request.POST.get("new_pw")
        confirm_pw = request.POST.get("confirm_pw")

        user = User.objects.get(id=request.user.id)
        if not user.check_password(old_pw):
            messages.error(request, "Wrong Old Password.")
            return redirect("/main/page/")
        if old_pw == new_pw:
            messages.error(request, "Same With Old Password. Cannot Be Used.")
            return redirect("/main/page/")
        if confirm_pw != new_pw:
            messages.error(request, "Password Unmatched.")
            return redirect("/main/page/")

        user.set_password(new_pw)
        user.save()
        messages.success(request, "Password Changed Successfully.")
        return redirect("/main/page/")


# ==========MAIN==========


@login_required(login_url="/")
def main(request):
    search = request.GET.get("search")
    categories = CategoryModel.objects.all().order_by("-created_at")
    products = ProductModel.objects.filter(is_active=True).order_by("-created_at")
    items = WishListModel.objects.filter(user=request.user)
    quantities = range(1, 100)

    if search:
        products = products.filter(
            Q(name__icontains=search)
            | Q(category__name__icontains=search)
            | Q(description__icontains=search)
        ).order_by("-created_at")

    paginator = Paginator(products, 17)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "main.html",
        {
            "products": page_obj,
            "categories": categories,
            "items": items,
            "quantities": quantities,
        },
    )


# ==========WISHLIST==========


@login_required(login_url="/")
def wishlist_add(request, id):
    product = ProductModel.objects.get(id=id)
    if request.method == "POST":
        if not request.user in product.reaction.all():
            product.reaction.add(request.user)
            item = WishListModel.objects.create(user=request.user, product=product)
            item.save()
            messages.success(request, "Added To Wishlist.")
        # else:
        #     product.reaction.remove(request.user)
        #     item = WishListModel.objects.filter(user=request.user, product=product)
        #     if item:
        #         item.delete()
        #     messages.error(request, "Removed From Wishlist.")
        return redirect("/main/page/")
    
@login_required(login_url="/")
def wishlist_delete(request, id):
    product = ProductModel.objects.get(id=id)
    if request.method == "POST":
        product.reaction.remove(request.user)
        item = WishListModel.objects.filter(user=request.user, product=product)
        if item:
            item.delete()
        messages.error(request, "Removed From Wishlist.")
    return redirect("/main/page/")

def wishlist_view(request):
    items = WishListModel.objects.filter(user=request.user)
    return render(request, "wishlist.html", {"items": items})


# ===============PRODUCT===============


@login_required(login_url="/")
def product_create(request):
    if not request.user.is_staff:
        return redirect("/main/page/")
    if request.method == "GET":
        return render(request, "workplace.html")
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        image = request.FILES.get("image")
        category = request.POST.get("category")
        product = ProductModel.objects.create(
            name=name,
            price=price,
            description=description,
            stock=stock,
            image=image,
            category_id=category,
        )
        product.save()
        messages.info(request, "Product Created.")
        return redirect("/work/place/")


@login_required(login_url="/")
def product_update(request, pk):
    if not request.user.is_staff:
        return redirect("/main/page/")
    product = ProductModel.objects.get(id=pk)
    if request.method == "GET":
        return render(request, "workplace.html", {"product": product})
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        description = request.POST.get("description")
        stock = request.POST.get("stock")
        image = request.FILES.get("image")
        category = request.POST.get("category")
        product.name = name
        product.price = price
        product.description = description
        product.stock = stock
        product.category_id = category
        if image:
            product.image.delete()
            product.image = image
        else:
            product.image = product.image
        product.save()
        messages.info(request, "Product Updated.")
        return redirect("/work/place/")


@login_required(login_url="/")
def product_delete(request, pk):
    if not request.user.is_staff:
        return redirect("/main/page/")
    product = ProductModel.objects.get(id=pk)
    if request.method == "GET":
        return render(request, "workplace.html", {"products": product})
    if request.method == "POST":
        if product.image:
            product.image.delete()
        product.delete()
        messages.error(request, "Product Deleted.")
    return redirect("/work/place/")


@login_required(login_url="/")
def product_detail(request, pk):
    product = ProductModel.objects.get(id=pk)
    return render(request, "main.html", {"product": product})


@login_required(login_url="/")
def product_list(request):
    if not request.user.is_staff:
        return redirect("/main/page/")
    search = request.GET.get("search")
    categories = CategoryModel.objects.all().order_by("-created_at")
    products = ProductModel.objects.all().order_by("-created_at")
    numbers = range(1, 100)

    if search:
        products = products.filter(
            Q(name__icontains=search)
            | Q(category__name__icontains=search)
            | Q(description__icontains=search)
        ).order_by("-created_at")

    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "product_count": ProductModel.objects.count(),
        "category_count": CategoryModel.objects.count(),
        "products": page_obj,
        "categories": categories,
        "numbers": numbers,
    }

    return render(request, "workplace.html", context)


# ===============CATEGORY===============


@login_required(login_url="/")
def category_create(request):
    if not request.user.is_staff:
        return redirect("/main/page/")
    if request.method == "GET":
        return render(request, "workplace.html")
    if request.method == "POST":
        name = request.POST.get("name")
        image = request.FILES.get("image")
        category = CategoryModel.objects.create(
            name=name,
            image=image,
        )
        category.save()
        messages.info(request, "Category Created.")
        return redirect("/work/place/")


@login_required(login_url="/")
def category_delete(request, pk):
    if not request.user.is_staff:
        return redirect("/main/page/")
    category = CategoryModel.objects.get(id=pk)
    if request.method == "GET":
        return render(request, "workplace.html", {"category": category})
    if request.method == "POST":
        if category.image:
            category.image.delete()
        category.delete()
        messages.error(request, "Category Deleted.")
        return redirect("/work/place/")


@login_required(login_url="/")
def category_list(request):
    if not request.user.is_staff:
        return redirect("/main/page/")
    categories = CategoryModel.objects.all()
    numbers = range(1, 100)
    paginator = Paginator(categories, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request, "workplace.html", {"categories": page_obj, "numbers": numbers}
    )


# ==========CONTACT==========


def contact(request):
    return render(request, "contact.html")


# ==========CART_LIST==========


@login_required(login_url="/")
def cart_add(request, id):
    product = ProductModel.objects.get(id=id)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        cart_item, created = CartListModel.objects.get_or_create(
            user=request.user,
            product=product,
        )

        if quantity > product.stock:
            quantity = product.stock

        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.stock:
                cart_item.quantity = product.stock
            else:
                cart_item.quantity = new_quantity
        else:
            cart_item.quantity = min(quantity, product.stock)

        cart_item.save()
        messages.success(request, "Item Added To Cart.")
        return redirect("/main/page/")


@login_required(login_url="/")
def cart_delete(request, id):
    cart_item = CartListModel.objects.get(id=id)
    if request.method == "GET":
        return render(request, "cart_list.html", {"cart_item": cart_item})
    if request.method == "POST":
        cart_item.delete()
        messages.error(request, "Item Removed From Cart.")
    return redirect("/cart/list/view/")


@login_required(login_url="/")
def cart_view(request):
    cart_items = CartListModel.objects.filter(user=request.user, is_ordered=False)
    overall_total = sum(cart_item.total_price() for cart_item in cart_items)
    context = {
        "cart_item_count": CartListModel.objects.filter(user=request.user).count(),
        "cart_items": cart_items,
        "overall_total": overall_total,
    }
    return render(request, "cart_list.html", context)


# ==========ORDER_LIST==========


@login_required(login_url="/")
def order_add(request, id):
    cart_item = CartListModel.objects.get(id=id)
    if request.method == "POST":
        order_item = OrderListModel.objects.create(
            user=request.user,
            cart_item=cart_item,
        )
        order_item.save()
        messages.success(request, "Order Placed Successfully.")
        cart_item.is_ordered = True
        cart_item.save()
        messages.success(request, "Item Hidden From Cart After Order Placement.")
        return redirect("/cart/list/view/")


@login_required(login_url="/")
def order_view(request):
    if not request.user.is_staff:
        return redirect("/main/page/")
    order_items = OrderListModel.objects.all()
    context = {
        "order_item_count": OrderListModel.objects.all().count(),
        "order_items": order_items,
    }
    return render(request, "order_list.html", context)
