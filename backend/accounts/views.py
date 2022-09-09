from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    SAFE_METHODS,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response(
            data={'message': f'Bye {request.user.username}!'},
            status=status.HTTP_204_NO_CONTENT
        )


# class LoginAPIView(APIView):
#     permission_classes = (SAFE_METHODS,)
#
#     def get(self, request, *args, **kwargs):
#         return Response(data=None)
#
#     def post(self, request, *args, **kwargs):
#         username = request.data.get("username", None)
#         password = request.data.get("password", None)
#
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 Response(
#                     data={
#                         "message": f"user <{username}> Logged In!",
#                     },
#                     status=status.HTTP_200_OK,
#                     content_type='application/json'
#                 )
#             else:
#                 return Response(
#                     data={
#                         "message": f"user <{username}> is not active!"
#                     },
#                     status=status.HTTP_405_METHOD_NOT_ALLOWED,
#                     content_type='application/json'
#                 )
#         else:
#             return Response(
#                 data={
#                     "message": "user not found"
#                 },
#                 status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
#                 content_type='application/json'
#             )


class UserRegistration(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response(
                data={
                    "username": serializer.data.get('username'),
                    'message': f"user {serializer.data.get('username')} has been saved!"
                },
                status=status.HTTP_201_CREATED,
                content_type='application/json',
            )
