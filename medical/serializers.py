from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .signals import order_created
from .models import Cart, CartItem, Patient, Order, OrderItem, Item, Collection, ItemImage, Review,Report,Feedback


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'items_count']

    items_count = serializers.IntegerField(read_only=True)


class ItemImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        item_id = self.context['item_id']
        return ItemImage.objects.create(item_id=item_id, **validated_data)

    class Meta:
        model = ItemImage
        fields = ['id', 'image']


class ItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'slug', 'inventory',
                  'unit_price', 'price_with_tax', 'collection', 'images']

    price_with_tax = serializers.SerializerMethodField(
        method_name='calculate_tax')

    def calculate_tax(self, item: Item):
        return item.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'name', 'description']

    def create(self, validated_data):
        item_id = self.context['item_id']
        return Review.objects.create(item_id=item_id, **validated_data)

class ReportSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'date', 'user_id', 'description']

    def create(self, validated_data):
        user_id = self.context['user_id']
        return Report.objects.create(user_id=user_id, **validated_data)

class FeedbackSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'date', 'user_id', 'description']

    def create(self, validated_data):
        user_id = self.context['user_id']
        return Feedback.objects.create(user_id=user_id, **validated_data)


class SimpleItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    item = SimpleItemSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.item.unit_price

    class Meta:
        model = CartItem
        fields = ['id', 'item', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.item.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField()

    def validate_item_id(self, value):
        if not Item.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No item with the given ID was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        item_id = self.validated_data['item_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, item_id=item_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'item_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class PatientSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user_id', 'phone', 'birth_date', 'membership']


class OrderItemSerializer(serializers.ModelSerializer):
    item = SimpleItemSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'unit_price', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'patient', 'placed_at', 'payment_status', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError(
                'No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('The cart is empty.')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            patient = Patient.objects.get(
                user_id=self.context['user_id'])
            order = Order.objects.create(patient=patient)

            cart_items = CartItem.objects \
                .select_related('item') \
                .filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    item=item.item,
                    unit_price=item.item.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)

            return order
