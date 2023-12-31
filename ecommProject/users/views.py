from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import UserSerializer


# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # Whenever we create a new user, the password they provide must be hashed, so we are hashing the password before
    # saving
    def perform_create(self, serializer):
        data = serializer.validated_data
        password = make_password(data['password'])
        serializer.save(password=password)

    # handling the update logic here...
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Extract the fields to update from request.data
        new_first_name = request.data.get('first_name')
        new_last_name = request.data.get('last_name')
        new_password = request.data.get('password')

        # Update the fields on the user instance
        instance.first_name = new_first_name
        instance.last_name = new_last_name

        if new_password:
            # Set the new password and save the instance
            instance.set_password(new_password)

        # Save the updated instance
        instance.save()

        return Response({'message': {new_first_name, new_last_name, new_password}})


# so what we are doing here, we need the user to authenticate using his/her email & password, and we are doing to modify
# the default user model (that will be a lot of work). So kind of duct tape fix, we are replacing the username field
# with the email using signals. [KIND OF DIRTY FIX, IK, BUT THAT WORKS !!!]
@receiver(pre_save, sender=User)
def update_username_with_email(sender, instance, **kwargs):
    user = instance
    if user.email != '':
        user.username = user.email
