from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from api.models import MyUser, Rol
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

Rol.objects.get_or_create(user_type='cliente')
Rol.objects.get_or_create(user_type='administrador')
Rol.objects.get_or_create(user_type='trabajador')

class RegisterView(generics.CreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        print(request.data)
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({'success': True, 'message': 'Usuario registrado con éxito'}, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            print(e)
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'success': False, 'message': 'Error interno del servidor, intente de nuevo'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class LogoutAndBlacklistRefreshTokenForUserView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({"message": "Token de actualización añadido a lista negra"}, status=status.HTTP_205_RESET_CONTENT)
            else:
                return Response({"error": "Token de actualización no proporcionado"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)