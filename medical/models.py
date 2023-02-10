from django.contrib import admin
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from uuid import uuid4

from medical.validators import validate_file_size


User = settings.AUTH_USER_MODEL


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_item = models.ForeignKey(
        'item', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']


class Item(models.Model):
    ITEM_TYPE_item = 'P'
    ITEM_TYPE_TREATMENT = 'T'

    ITEM_TYPE_CHOICES = [
        (ITEM_TYPE_item, 'item'),
        (ITEM_TYPE_TREATMENT, 'Treatment'),
    ]

    membership = models.CharField(
        max_length=1, choices=ITEM_TYPE_CHOICES, default=ITEM_TYPE_item)
   
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=True)
    description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(1)]
    )
    inventory = models.IntegerField(validators=[MinValueValidator(1)])
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.PROTECT, related_name='items')


    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ['title']




class ItemImage(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='medical/images',
                              validators=[validate_file_size])


class Patient(models.Model):
  
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        permissions = [
            ('view_history', 'Can View History')
        ]

    @admin.display(ordering='first_name')
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering='last_name')
    def last_name(self):
        return self.user.last_name


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CANCEL = 'X'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
        (PAYMENT_STATUS_CANCEL, 'Cancel'),

    ]

    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    placed_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(
        Patient, on_delete=models.PROTECT)  # never delete order

    class Meta:
        permissions = [
            ('cancel_order', 'Can Cancel Order')
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT, related_name='items')
    item = models.ForeignKey(
        Item, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    # If the patient has multiple addresses
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    post_code = models.SmallIntegerField(null=True)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together = [['cart', 'item']]


class Review(models.Model):
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)


class Report(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reports')
    description = models.TextField()
    date = models.DateField(auto_now_add=True)

class Feedback(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='feedbacks')
    description = models.TextField()
    date = models.DateField(auto_now_add=True)


