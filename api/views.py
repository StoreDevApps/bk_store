from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from api.models import CarouselImage, MyUser, Rol, ProductCategory, Product
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import base64
import os

Rol.objects.get_or_create(user_type="cliente")
Rol.objects.get_or_create(user_type="administrador")
Rol.objects.get_or_create(user_type="trabajador")


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
            return Response(
                {"success": True, "message": "Usuario registrado con éxito"},
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        except ValidationError as e:
            print(e)
            return Response(
                {"success": False, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "success": False,
                    "message": "Error interno del servidor, intente de nuevo",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutAndBlacklistRefreshTokenForUserView(generics.CreateAPIView):
    '''
    Logout and blacklist refresh token for user
    '''
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response(
                    {"message": "Token de actualización añadido a lista negra"},
                    status=status.HTTP_205_RESET_CONTENT,
                )
            else:
                return Response(
                    {"error": "Token de actualización no proporcionado"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ListOfProductsWithoutLoginView(generics.ListAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.all()
        products_list = []
        for product in products:
            products_list.append(
                {
                    "detail": product.detail,
                    "brand": product.brand,
                    "category_name": product.category.name,
                    "id": product.id,
                    "url": product.url,
                }
            )

        return Response(
            {"success": True, "products": products_list}, status=status.HTTP_200_OK
        )


class EmailContactUs(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        name = request.data.get("name")
        message = request.data.get("message")

        full_message = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        try:
            mail = EmailMultiAlternatives(
                subject="Correo enviado desde Store Online",
                body=full_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.EMAIL_HOST_USER],
            )
            mail.send()
            return Response({"success": True}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(
                {"success": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ListOfProductCategoryView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        product_categories = ProductCategory.objects.all()
        product_categories_list = []
        for product_category in product_categories:
            product_categories_list.append(
                {"name": product_category.name, "id": product_category.id}
            )

        return Response(
            {"success": True, "product_categories": product_categories_list},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        try:
            product_category = ProductCategory(name=name)
            product_category.save()
            return Response(
                {"success": True, "message": "Categoría creada correctamente"},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "success": False,
                    "message": "Error interno del servidor, intente de nuevo",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProductCategoryView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            product_category = ProductCategory.objects.get(id=pk)
            return Response(
                {
                    "success": True,
                    "product_category": {
                        "name": product_category.name,
                        "id": product_category.id,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "success": False,
                    "message": "Error interno del servidor, intente de nuevo",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        name = request.data.get("name")
        try:
            product_category = ProductCategory.objects.get(id=pk)
            product_category.name = name
            product_category.save()
            return Response(
                {"success": True, "message": "Categoría actualizada correctamente"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "success": False,
                    "message": "Error interno del servidor, intente de nuevo",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            product_category = ProductCategory.objects.get(id=pk)
            product_category.delete()
            return Response(
                {"success": True, "message": "Categoría eliminada correctamente"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "success": False,
                    "message": "Error interno del servidor, intente de nuevo",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ListOfProductsView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.all()
        products_list = []
        for product in products:
            products_list.append(
                {
                    "presentation": product.presentation,
                    "category": product.category.name,
                    "detail": product.detail,
                    "brand": product.brand,
                    "codigo": product.codigo,
                    "duedate": product.duedate,
                    "url": product.url,
                }
            )

        return Response(
            {"success": True, "products": products_list}, status=status.HTTP_200_OK
        )


class CarouselImageHomeView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        carousel_images = CarouselImage.objects.all()
        carousel_images_list = []

        for carousel_image in carousel_images:
            # Ensure the URL is safe and construct the file path
            file_name = carousel_image.url.lstrip("/")
            file_path = os.path.join(
                settings.STATICFILES_DIRS[0], "carousel_home", file_name
            )

            # Ensure the file path is within the static files directory
            if (
                not os.path.commonpath([settings.STATICFILES_DIRS[0], file_path])
                == settings.STATICFILES_DIRS[0]
            ):
                return Response(
                    {"error": "Archivo fuera de los límites permitidos"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Read and encode the image in base64
            try:
                with open(file_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                    image_data = f"data:image/jpeg;base64,{encoded_image}"
                    carousel_images_list.append(
                        {"url": image_data, "name": carousel_image.url}
                    )
            except FileNotFoundError:
                # Handle the case where the file is not found
                carousel_images_list.append(
                    {"url": "data:image/jpeg;base64,"}
                )  # Empty placeholder

        return Response(
            {"success": True, "carousel_images": carousel_images_list},
            status=status.HTTP_200_OK,
        )
