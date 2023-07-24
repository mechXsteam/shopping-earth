from rest_framework import serializers

from api_01.models import Product, Order, OrderItem, Review


class ReviewProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


# product serializer: A serializer is a class which converts querysets into JSON
class ProductSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    review = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    # gets username of the user (means who added this product to
    # the database, may be the name of the company), before that we had a user_id which was not very
    # helpful
    def get_user(self, obj):
        return f"{obj.user}"

    # get all reviews associated with a product
    def get_review(self, obj):
        review = obj.review_set.all()
        serializer = ReviewProductSerializer(review, many=True)
        return serializer.data


class CreateOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class CreateOrderSerializer(serializers.ModelSerializer):
    orderItems = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_orderItems(self, obj):
        items = obj.orderitem_set.all()
        serializer = CreateOrderItemSerializer(items, many=True)
        return serializer.data
