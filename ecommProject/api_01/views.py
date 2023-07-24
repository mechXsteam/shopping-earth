from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Product, Order, OrderItem, Review
from .serializers import ProductSerializer, CreateOrderSerializer, CreateOrderItemSerializer, ReviewProductSerializer


# Create your views here.

# CRUD products
class ProductViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    # queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'  # now with this param, our individual product will be fetched. earlier it was the id.

    # handles the search logic
    def get_queryset(self):
        # <QueryDict: {'': ['mobile']}>, so i need to access the query params using '' keyword. The URL with which I am
        # trying to access the query set is http://localhost:8000/api_01/?=${keyword}, if anyone in the readers knows
        # the solution for it, please let me know.
        query_dict = self.request.query_params
        if len(query_dict) != 0:
            query = query_dict['']
        else:
            query = ''  # without this else statement, the query would be None, and we may run into some unwanted
            # errors. "" matches with every thing.
        return Product.objects.filter(name__icontains=query)


# PLAN OF ACTION:
# We are sending data to this following view set from the frontend, such as order details, order items. The data sent
# is recievable in request argument (print(request.data) to see...). First we create the order object (because all
# other models are some kind of dependent on it), after that we attach the ordered items in the cart to the order object.
# Since some kind of order has been added to the order hence an equal amount of products must be subtracted from the
# stock.
class CreateOrderViewSet(viewsets.ModelViewSet):
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]

    # filtering the list of orders
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.id)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data

        orderItems = data.get('orderItems', [])
        # if somehow user has access to our cart, the user cannot make an order with an empty cart.
        if not orderItems:
            return Response({'detail': 'No Order Items'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # create the order
            order = Order.objects.create(
                user=user,
                taxPrice=data['taxPrice'],
                shippingPrice=data['shippingPrice'],
                totalPrice=data['totalPrice'],
                address=data['shippingAddress']['address1'] + " , " + data['shippingAddress']['address2'],
                city=data['shippingAddress']['city'],
                postalCode=data['shippingAddress']['zip'],
                state=data['shippingAddress']['state'],
            )

            for ele in orderItems:
                product = Product.objects.get(id=ele['product']['id'])

                item = OrderItem.objects.create(
                    product=product,
                    order=order,
                    name=product.name,
                    qty=ele['qty'],
                    price=ele['product']['price'],
                    image=ele['product']['image'],
                )

                # (4) Update stock

                product.countInStock -= item.qty
                product.save()
            serializer = CreateOrderSerializer(order, many=False)
            return Response({'order id': serializer.data['id']})


class CreateOrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = OrderItem.objects.all()
    serializer_class = CreateOrderItemSerializer


class ReviewProductViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewProductSerializer
    queryset = Review.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def create(self, request, *args, **kwargs):
        user = request.user
        product = Product.objects.get(id=self.request.data['product_id'])
        data = request.data

        review = Review.objects.create(
            user=user,
            product=product,
            name=user.first_name,
            rating=data['rating'],
            comment=data['comment'],
        )

        reviews = product.review_set.all()
        product.numReviews = len(reviews)

        total = 0
        for i in reviews:
            total += i.rating

        product.rating = total / len(reviews)
        product.save()

        return Response('Review Added')


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims: these data will be encrypted in the jwt decode
        token['username'] = user.username
        token['email'] = user.email
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name

        return token

    # we can overide the validate method to include a bunch of other things such as email, username, staff status
    # in addition to the default access_token and refresh_token

    # def validate(self, attrs: dict[str, any]) -> dict[str, str]:
    #     data = super().validate(attrs)
    #
    #     refresh = self.get_token(self.user)
    #
    #     data["username"] = str(self.user.username)
    #     # data["email"] = str(self.user.email)
    #     data["first_name"] = str(self.user.first_name)
    #     data["last_name"] = str(self.user.last_name)
    #
    #     return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
