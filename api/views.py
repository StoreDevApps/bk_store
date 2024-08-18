import base64
import json
import os
import random
import string
import traceback

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView


from api.models import (
    CarouselImage,
    CategoriesService,
    CodigosReestablecimiento,
    MyUser,
    Product,
    ProductCategory,
    ProductImage,
    Rol,
    Service,
)

from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer


def get_rol_client():
    return Rol.objects.get_or_create(user_type="usuario")[0]


def get_rol_admin():
    return Rol.objects.get_or_create(user_type="administrador")[0]


def get_rol_worker():
    return Rol.objects.get_or_create(user_type="trabajador")[0]


MENSAJE_ERROR_500 = "Error interno del servidor, intente de nuevo"
MENSAJ_ERROR_NO_ACCESO_CARPETA = "Archivo fuera de los límites permitidos"


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
                    "message": MENSAJE_ERROR_500,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutAndBlacklistRefreshTokenForUserView(generics.CreateAPIView):
    """
    Logout and blacklist refresh token for user
    """

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
        except Exception:
            return Response(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class EnviarCodigo(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        correo = request.data["correo"]
        try:
            usuario = MyUser.objects.get(email=correo)
            codigo = "".join(random.choice("0123456789") for _ in range(4))
            tiempo = timezone.now()
            registro = CodigosReestablecimiento(
                idUsuario=usuario, codigo=codigo, tiempoCreacion=tiempo
            )
            registro.save()
            template = get_template("codigo.html")
            # Se renderiza el template y se envian parametros
            content = template.render({"codigo": codigo})

            msg = EmailMultiAlternatives(
                subject="Reestablecer contraseña",
                body="Hola, recuerda que tu codigo tiene una duracion de 10min",
                from_email=settings.EMAIL_HOST_USER,
                to=[correo],
            )
            msg.attach_alternative(content, "text/html")
            msg.send()
            message = (
                "Se ha enviado el código a su correo. Por favor revíselo y "
                "también a la mano para poder cambiar su contraseña."
            )
            return Response(
                {
                    "success": True,
                    "message": message,
                    "codigo": codigo,
                }
            )
        except MyUser.DoesNotExist:
            print(traceback.format_exc())
            return Response(
                {"success": False, "error": "Correo no valido, su cuenta no existe"},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception:
            print(traceback.format_exc())
            return Response(
                {
                    "success": False,
                    "error": "Error intern o del servidor, intentalo de nuevo",
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class VerificarCodigo(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            codigo_ingresado = request.data["codigo"]
            correo = request.data["correo"]
            usuario = MyUser.objects.filter(email=correo).first()
            registro = (
                CodigosReestablecimiento.objects.filter(idUsuario=usuario)
                .order_by("-tiempoCreacion")
                .first()
            )
            tiempo = (timezone.now() - registro.tiempoCreacion).total_seconds() <= 600
            if (
                registro
                and registro.codigo == codigo_ingresado
                and not registro.isUtilizado
                and tiempo
            ):
                registro.isUtilizado = True
                registro.save()
                return Response(
                    {"success": True, "status": 200, "usuario": usuario.to_json()}
                )
            elif registro.codigo != codigo_ingresado:
                return Response(
                    {"success": False, "mensaje": "Código ingresado no válido"}
                )
            elif not tiempo:
                return Response({"success": False, "mensaje": "Código ha expirado"})
            else:
                return Response(
                    {"success": False, "mensaje": "No existe ningun registro"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception:
            return Response(
                {
                    "success": False,
                    "error": MENSAJE_ERROR_500,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ReestablecerContrasena(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return self._reestablecer_contrasena(request, reset_password=True)

    def put(self, request):
        return self._reestablecer_contrasena(request, reset_password=False)

    def _reestablecer_contrasena(self, request, reset_password):
        try:
            correo = request.data.get("correo")
            usuario = MyUser.objects.get(email=correo)

            if not reset_password:
                actual_contrasena = request.data.get("actualPassword")
                if not usuario.check_password(actual_contrasena):
                    return Response(
                        {"success": False, "message": "Contraseña actual incorrecta"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            nueva_contrasena = request.data.get("newPassword")
            if usuario.check_password(nueva_contrasena):
                return Response(
                    {
                        "success": False,
                        "message": "La nueva contraseña debe ser diferente de la actual",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            usuario.set_password(nueva_contrasena)
            usuario.save()

            return Response(
                {"success": True, "usuario": usuario.to_json()},
                status=status.HTTP_200_OK,
            )
        except MyUser.DoesNotExist:
            return Response(
                {"success": False, "message": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            return Response(
                {
                    "success": False,
                    "error": MENSAJE_ERROR_500,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ListOfProductsWithoutLoginView(generics.ListAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.all()
        products_list = []
        products_list = [product.to_json() for product in products]

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
                    "message": MENSAJE_ERROR_500,
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
                    "message": MENSAJE_ERROR_500,
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
                    "message": MENSAJE_ERROR_500,
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
                    "message": MENSAJE_ERROR_500,
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
            file_name = carousel_image.url.lstrip("/")
            file_path = os.path.join(
                settings.STATICFILES_DIRS[0], "carousel_home", file_name
            )

            if (
                os.path.commonpath([settings.STATICFILES_DIRS[0], file_path])
                != settings.STATICFILES_DIRS[0]
            ):
                return Response(
                    {"success": False, "error": MENSAJ_ERROR_NO_ACCESO_CARPETA},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                with open(file_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                    image_data = f"data:image/jpeg;base64,{encoded_image}"
                    carousel_images_list.append(
                        {
                            "url": image_data,
                            "name": carousel_image.name,
                            "id": carousel_image.id,
                        }
                    )
            except FileNotFoundError:
                carousel_images_list.append({"url": "data:image/jpeg;base64,"})

        return Response(
            {"success": True, "carousel_images": carousel_images_list},
            status=status.HTTP_200_OK,
        )


class UploadCarouselImageView(generics.ListCreateAPIView):
    def post(self, request):
        file_data_list = request.POST.getlist("fileData[]")
        images = request.FILES.getlist("images[]")

        for i, file_data_json in enumerate(file_data_list):
            file_data = json.loads(file_data_json)

            # Obtener los datos del JSON
            file_name_without_extension = file_data["name"]
            unique_name_with_extension = file_data["uniqueNameWithExtension"]

            # Obtener la imagen correspondiente del request.FILES
            image = images[i]

            if image:
                file_path = os.path.join(
                    settings.STATICFILES_DIRS[0],
                    "carousel_home",
                    unique_name_with_extension,
                )

                # Asegúrate de que el directorio existe
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Guardar la imagen en la ruta especificada
                with open(file_path, "wb") as f:
                    f.write(image.read())

                # Guardar la información en la base de datos
                CarouselImage(
                    name=file_name_without_extension, url=unique_name_with_extension
                ).save()
            else:
                return Response(
                    {"success": False, "message": "Error al cargar la imagen"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {"success": True, "message": "Imagenes guardadas correctamente"},
            status=status.HTTP_200_OK,
        )


class DeleteCarouselImageView(generics.ListCreateAPIView):
    def delete(self, request, pk):
        try:
            carousel_image = CarouselImage.objects.get(id=pk)

            image_path = os.path.join(
                settings.STATICFILES_DIRS[0], "carousel_home", carousel_image.url
            )

            # Eliminar el archivo del sistema de archivos si existe
            if os.path.exists(image_path):
                os.remove(image_path)

            carousel_image.delete()
            return Response(
                {"success": True, "message": "Imagen eliminada correctamente"},
                status=status.HTTP_200_OK,
            )

        except CarouselImage.DoesNotExist:
            return Response(
                {"success": False, "message": "Imagen no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(e)
            return Response(
                {
                    "success": False,
                    "message": MENSAJE_ERROR_500,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminCategoriesServicesView(generics.ListCreateAPIView):
    def get(self, request):
        categories = CategoriesService.objects.all()
        categories_list = []

        for category in categories:
            categories_list.append({"name": category.name})

        return Response(
            {"success": True, "categories": categories_list}, status=status.HTTP_200_OK
        )

    def post(self, request):
        name = request.data.get("name")
        print(name)
        try:
            CategoriesService(name=name).save()
            return Response(
                {"success": True, "message": "Categoría guardada correctamente"},
                status=status.HTTP_200_OK,
            )
        except Exception:
            print(traceback.format_exc())
            return Response(
                {
                    "success": False,
                    "message": MENSAJE_ERROR_500,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PublicServicesView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    def get(self, request):
        services = Service.objects.all()
        services_list = {}

        for service in services:
            file_name = service.url.lstrip("/")
            file_path = os.path.join(
                settings.STATICFILES_DIRS[0], "services", file_name
            )
            # Ensure the file path is within the static files directory
            if (
                os.path.commonpath([settings.STATICFILES_DIRS[0], file_path])
                != settings.STATICFILES_DIRS[0]
            ):
                return Response(
                    {"error": MENSAJ_ERROR_NO_ACCESO_CARPETA},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                with open(file_path, "rb") as f:
                    encoded_image = base64.b64encode(f.read()).decode("utf-8")
                    image_data = f"data:image/jpeg;base64,{encoded_image}"
            except FileNotFoundError:
                # Handle the case where the file is not found
                image_data = "data:image/jpeg;base64,"  # Empty placeholder
            current = {
                "name": service.name,
                "description": service.description,
                "image": image_data,
            }
            if service.categoria.name not in services_list:
                services_list[service.categoria.name] = [current]
            else:
                services_list[service.categoria.name].append(current)
        return Response(
            {"success": True, "services": services_list}, status=status.HTTP_200_OK
        )


class AdminServicesView(generics.ListCreateAPIView):

    def get(self, request):
        services = Service.objects.all()
        services_list = []

        for service in services:

            file_name = service.url.lstrip("/")

            file_path = os.path.join(
                settings.STATICFILES_DIRS[0], "services", file_name
            )

            if (
                os.path.commonpath([settings.STATICFILES_DIRS[0], file_path])
                != settings.STATICFILES_DIRS[0]
            ):
                return Response(
                    {"success": False, "error": MENSAJ_ERROR_NO_ACCESO_CARPETA},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                with open(file_path, "rb") as f:
                    encoded_image = base64.b64encode(f.read()).decode("utf-8")
                    image_data = f"data:image/jpeg;base64,{encoded_image}"
            except FileNotFoundError:
                image_data = "data:image/jpeg;base64,"

            services_list.append(
                {
                    "id": service.id,
                    "name": service.name,
                    "category": service.categoria.name,
                    "image": image_data,
                    "description": service.description,
                }
            )

        return Response(
            {"success": True, "services": services_list}, status=status.HTTP_200_OK
        )

    def post(self, request):
        print(request.POST.get("service"))
        service_data = json.loads(request.data.get("service"))
        print("******************************")
        print(request.data.get("fileData"))
        file_data = json.loads(request.data.get("fileData"))
        image = request.FILES.get("image")

        if image:
            file_path = os.path.join(
                settings.STATICFILES_DIRS[0],
                "services",
                file_data["uniqueNameWithExtension"],
            )

            # Asegúrate de que el directorio existe
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Guardar la imagen en la ruta especificada
            with open(file_path, "wb") as f:
                f.write(image.read())

            categoria = CategoriesService.objects.get(name=service_data["category"])

            service = Service(
                name=service_data["name"],
                categoria=categoria,
                url=file_data["uniqueNameWithExtension"],
                description=service_data["description"],
            )
            service.save()
        else:
            return Response(
                {"success": False, "message": "No se ha cargado ninguna imagen"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"success": True, "message": "Servicio creado correctamente"},
            status=status.HTTP_200_OK,
        )


class AdminServiceView(generics.ListCreateAPIView):
    def put(self, request, pk):
        try:
            print("pk", pk)
            service_data = json.loads(request.data.get("service"))
            print(service_data)
            service = Service.objects.get(id=pk)
            print(service)
            image = request.FILES.getlist("image")

            print(image)
            unique_name_with_extension = service.url

            if image:
                image = image[0]
                file_data = json.loads(request.data.get("fileData"))
                unique_name_with_extension = file_data["uniqueNameWithExtension"]

                image_path = os.path.join(
                    settings.STATICFILES_DIRS[0], "services", service.url
                )

                if os.path.exists(image_path):
                    os.remove(image_path)

                file_path = os.path.join(
                    settings.STATICFILES_DIRS[0], "services", unique_name_with_extension
                )

                # Asegúrate de que el directorio existe
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                # Guardar la imagen en la ruta especificada
                with open(file_path, "wb") as f:
                    f.write(image.read())

                service.url = unique_name_with_extension

            service.name = service_data["name"]
            service.description = service_data["description"]
            service.categoria = CategoriesService.objects.get(
                name=service_data["category"]
            )
            service.save()

            return Response(
                {"success": True, "message": "Servicio actualizado correctamente"},
                status=status.HTTP_200_OK,
            )
        except Service.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": MENSAJE_ERROR_500,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            service = Service.objects.get(id=pk)

            image_path = os.path.join(
                settings.STATICFILES_DIRS[0], "services", service.url
            )

            # Eliminar el archivo del sistema de archivos si existe
            if os.path.exists(image_path):
                os.remove(image_path)

                service.delete()
                return Response(
                    {"success": True, "message": "Servicio eliminado correctamente"},
                    status=status.HTTP_200_OK,
                )

            else:
                return Response(
                    {"success": False, "message": "Servicio no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Service.DoesNotExist:
            return Response(
                {"success": False, "message": "Servicio no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception:
            return Response(
                {
                    "success": False,
                    "message": MENSAJE_ERROR_500,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserWorkerListView(generics.CreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = RegisterSerializer

    def get(self, request):
        current = MyUser.objects.get(id=request.user.id)
        workers_list = []
        if current.rol == get_rol_admin():
            workers = MyUser.objects.filter(rol=get_rol_worker(), is_active=True).all()
            for worker in workers:
                workers_list.append(
                    {
                        "name": worker.name,
                        "last_name": worker.last_name,
                        "email": worker.email,
                        "phone_number": worker.phone_number,
                    }
                )
        else:
            return Response(
                {"success": False, "message": "Acceso denegado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {"success": True, "workers": workers_list}, status=status.HTTP_200_OK
        )

    def post(self, request):
        current = MyUser.objects.get(id=request.user.id)
        if current.rol == get_rol_admin():
            try:
                worker_data = request.data
                if MyUser.objects.filter(email=worker_data["email"]).exists():
                    return Response(
                        {"success": False, "message": "Correo ya registrado"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                worker_data["password"] = self.generate_random_password()
                worker_data["rol"] = get_rol_worker().user_type
                serializer = self.get_serializer(data=worker_data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                user_email = worker_data["email"]
                user_password = worker_data["password"]
                mail = EmailMultiAlternatives(
                    subject="Su cuenta ha sido creada",
                    body=(
                        f"Su usuario es: {user_email} y su contraseña temporal es: "
                        f"{user_password}. Por favor cambie su contraseña lo más pronto posible."
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    to=[user_email],
                )
                mail.send()

                return Response(
                    {"success": True, "message": "Trabajador creado correctamente"},
                    status=status.HTTP_200_OK,
                )
            except ValidationError as e:
                print(traceback.format_exc())
                return Response(
                    {"success": False, "message": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception:
                print(traceback.format_exc())
                return Response(
                    {
                        "success": False,
                        "message": MENSAJE_ERROR_500,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"success": False, "message": "Acceso denegado"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def generate_random_password(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        random_password = "".join(random.choice(characters) for i in range(length))
        return random_password


class WorkerToAdminView(generics.CreateAPIView):

    def post(self, request):
        current = MyUser.objects.get(id=request.user.id)
        if current.rol == get_rol_admin():
            try:
                worker_email = request.data["email"]
                worker = MyUser.objects.get(email=worker_email)
                worker.rol = get_rol_admin()
                worker.save()

                return Response(
                    {"success": True, "message": "Administrador creado correctamente"},
                    status=status.HTTP_200_OK,
                )

            except MyUser.DoesNotExist:
                return Response(
                    {"success": False, "message": "Trabajador no encontrado"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            except Exception:
                return Response(
                    {
                        "success": False,
                        "message": MENSAJE_ERROR_500,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )


class GetMultimediaProductoView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        try:
            # Get the product
            product = Product.objects.get(id=product_id)

            # Get the images and videos associated with the product
            images = product.images.all()
            videos = product.videos.all()

            # Construct the JSON response
            multimedia = {
                "product": product.detail,
                "images": [
                    {
                        "id": image.id,
                        "url": (
                            image.url
                            if image.url
                            else request.build_absolute_uri(image.image.url)
                        ),
                    }
                    for image in images
                ],
                "videos": [{"id": video.id, "url": video.url} for video in videos],
            }

            return Response(
                {"success": True, "multimedia": multimedia}, status=status.HTTP_200_OK
            )

        except Product.DoesNotExist:
            return Response(
                {"success": False, "message": "Producto no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            print(e)
            return Response(
                {"success": False, "message": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ListadoProductosView(APIView):

    def get(self, request):
        products = Product.objects.all()
        products_list = [product.to_json() for product in products]
        return Response(
            {"success": True, "products": products_list}, status=status.HTTP_200_OK
        )

    def post(self, request):
        product = Product()
        codigo = request.data.get("codigo")
        detail = request.data.get("detail")
        presentation = request.data.get("presentation")
        category = request.data.get("category")
        brand = request.data.get("brand")
        units = request.data.get("units")
        duedate = request.data.get("duedate")

        try:
            category = ProductCategory.objects.get(name=category)

            product.codigo = codigo
            product.detail = detail
            product.presentation = presentation
            product.category = category
            product.brand = brand
            product.units = units
            product.duedate = duedate
            product.save()
            return Response(
                {"success": True, "message": "Producto creado correctamente"},
                status=status.HTTP_200_OK,
            )

        except ProductCategory.DoesNotExist:
            return Response(
                {"success": False, "message": "Categória no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            print(e)
            return Response(
                {"success": False, "message": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        id = request.data.get("id")
        codigo = request.data.get("codigo")
        detail = request.data.get("detail")
        presentation = request.data.get("presentation")
        category = request.data.get("category")
        brand = request.data.get("brand")
        units = request.data.get("units")
        duedate = request.data.get("duedate")
        print(request.data)

        try:
            category = ProductCategory.objects.get(name=category)
            product = Product.objects.get(id=id)
            product.codigo = codigo
            product.detail = detail
            product.presentation = presentation
            product.category = category
            product.brand = brand
            product.units = units
            product.duedate = duedate
            product.save()
            return Response(
                {"success": True, "message": "Producto actualizado correctamente"},
                status=status.HTTP_200_OK,
            )

        except Product.DoesNotExist:
            return Response(
                {"success": False, "message": "Producto no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except ProductCategory.DoesNotExist:
            return Response(
                {"success": False, "message": "Categoria no encontrada"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            print(e)
            return Response(
                {"success": False, "message": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request):
        id = request.data.get("id")
        try:
            product = Product.objects.get(id=id)
            product.delete()
            return Response(
                {"success": True, "message": "Producto eliminado correctamente"},
                status=status.HTTP_200_OK,
            )

        except Product.DoesNotExist:
            return Response(
                {"success": False, "message": "Producto no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            print(e)
            return Response(
                {"success": False, "message": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ImagenesProductoView(APIView):

    def post(self, request):
        try:
            images = request.FILES.getlist("images[]")
            product_id = request.data["product_id"]
            product = Product.objects.get(id=product_id)
            for image in images:
                ProductImage.objects.create(product=product, image=image)
            return Response(
                {"success": True, "message": "Imagenes guardadas correctamente"},
                status=status.HTTP_200_OK,
            )

        except Product.DoesNotExist:
            return Response(
                {"success": False, "message": "Producto no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            print(e)
            return Response(
                {"success": False, "message": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteProductImageView(APIView):
    def delete(self, request, product_id):
        image_url = request.data.get("url")
        product = Product.objects.get(id=product_id)
        print(image_url)
        print(ProductImage.objects.filter(product=product, image=image_url))
        product_images = ProductImage.objects.filter(product=product)
        for image in product_images:
            if image.image.url == image_url:
                print(image.image.url)
                print(image_url)
                image.delete()
                return Response(
                    {"message": "Imagen eliminada exitosamente"},
                    status=status.HTTP_200_OK,
                )
        else:
            return Response(
                {"error": "Imagen no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )


class ProductoView(APIView):

    def put(self, request, product_id):
        return Response(
            {"success": True, "message": "Success"}, status=status.HTTP_200_OK
        )
