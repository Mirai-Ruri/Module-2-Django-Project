from django.db import models
from django.contrib.auth.models import User
from .base_models import TimeStampedModel

# Create your models here.


class ProfileModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(
        upload_to="user_profile_images",
        null=True,
        blank=True,
        default="user_profile_images/default_profile.png",
    )


class CategoryModel(TimeStampedModel):
    name = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to="category_images",
        null=True,
        blank=True,
        default="category_images/default_product.png",
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class ProductModel(TimeStampedModel):
    name = models.CharField(max_length=200)
    price = models.IntegerField(default=0)
    description = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to="product_images",
        null=True,
        blank=True,
        default="product_images/default_product.png",
    )
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(
        CategoryModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    reaction = models.ManyToManyField(User, blank=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


class WishListModel(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "WishList"
        verbose_name_plural = "WishLists"
        unique_together = ("user", "product")  # prevents duplicates

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class CartListModel(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    is_ordered = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    def total_price(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.quantity}"


class OrderListModel(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart_item = models.ForeignKey(
        CartListModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Order List"
        verbose_name_plural = "Order Lists"

    def __str__(self):
        return f"{self.user.username} - {self.cart_item.product.name} - {self.cart_item.quantity} items"


class MessageModel(TimeStampedModel):
    user_message = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        if self.author:
            return f"{ self.author.username } sent a message"
        else:
            return "Anonymous sent a message."
