from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from api.managers import MyUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Avg, Count
from django.db.models import Q

class Rol(models.Model):
    '''
    Modelo de rol de usuario
    
    params:
        - user_type (str)
    
    '''
    user_type = models.CharField(max_length=30)

    def __str__(self):
        return str(self.user_type)


class MyUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.email)

    def to_json(self):
        return {
            "name": self.name,
            "last_name": self.last_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "rol_user_type": self.rol.user_type,
            "is_active": self.is_active,
            "is_staff": self.is_staff,
        }
    

    def ha_comprado(self, producto):
        """
        Verifica si el usuario ha comprado un producto específico.
        Solo cuenta las órdenes con estado 'Completa'.
        """
        return Orden.objects.filter(
            usuario=self,
            estado='Completa',
            items__producto=producto
        ).exists()
        


class ProductCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.name)
    
class CategoriesService(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.name)


class Suplier(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=150, unique=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    direction = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return str(self.name)


def validate_image_size(image):
    max_size_mb = 4
    if image.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _(f"Image file size should not exceed {max_size_mb}MB.")
        )


class Product(models.Model):
    presentation = models.CharField(max_length=30)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    detail = models.CharField(max_length=70)
    brand = models.CharField(max_length=30)
    codigo = models.CharField(max_length=30, unique=True)
    duedate = models.DateField(blank=True, null=True)
    state = models.CharField(max_length=1, default='A')
    aud_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.detail) + " (" + self.brand + ")"

    def has_commented(self, user):
        return Comentario.objects.filter(usuario=user, producto=self).exists()

    def to_json(self):
            # Obtener el último registro de historial de compras
            last_history = self.producthistory_set.order_by('-date').first()
            price = last_history.unit_sales_price if last_history else None
            average_rating, rating_count = self.calcular_puntuacion_promedio()


            # Recopilar imágenes
            images = [image.url or image.image.url for image in self.images.all() if image.url or image.image]
            # Recopilar videos
            videos = [video.url for video in self.videos.all() if video.url]

            return {
                "id": self.id,
                "presentation": self.presentation,
                "category": self.category.name,
                "detail": self.detail,
                "brand": self.brand,
                "codigo": self.codigo,
                "duedate": self.duedate,
                "state": self.state,
                "aud_created_at": self.aud_created_at.isoformat() if self.aud_created_at else None,
                "images": images,
                "videos": videos,
                "price": price  # Incluye el precio en el JSON
            }

    def calcular_puntuacion_promedio(self):
        promedio = Comentario.objects.filter(producto=self).aggregate(
            average=Avg('puntuacion'),
            count=Count('puntuacion')
        )
        average_rating = promedio['average'] if promedio['average'] is not None else 0
        count = promedio['count'] if promedio['count'] is not None else 0
        return average_rating, count
    
    def user_has_purchased(self, user):
        """
        Verifica si el usuario ha comprado el producto.
        """
        return DetalleOrden.objects.filter(
            Q(orden__usuario=user) & 
            Q(orden__estado='Completada') & 
            Q(producto=self)
        ).exists()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    url = models.TextField(blank=True, null=True)  # Allows very long URLs
    image = models.ImageField(upload_to='public/product_images/', validators=[validate_image_size], blank=True, null=True)

    def __str__(self):
        return str(self.url or self.image.url)

    def save(self, *args, **kwargs):
        if not (self.url or self.image):
            raise ValidationError('Either an image or a URL must be provided.')
        super().save(*args, **kwargs)


class ProductVideo(models.Model):
    product = models.ForeignKey(Product, related_name="videos", on_delete=models.CASCADE)
    url = models.URLField(max_length=200)

    def __str__(self):
        return str(self.url)
    product = models.ForeignKey(Product, related_name="videos", on_delete=models.CASCADE)
    url = models.URLField(max_length=200)

    def __str__(self):
        return str(self.url)

class ProductHistory(models.Model):
    date = models.DateField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    suplier = models.ForeignKey(Suplier, on_delete=models.CASCADE)
    unit_cost_price = models.FloatField()
    unit_sales_price = models.FloatField()
    units_purchased = models.IntegerField(default=0)

    def __str__(self):
        return str(self.product) + " - " + str(self.suplier) + " - " + str(self.date)


class Inventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sales_price = models.FloatField()

    def __str__(self):
        return (
            str(self.product)
            + " - "
            + str(self.quantity)
            + " - "
            + str(self.sales_price)
        )


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date = models.DateField()

    def __str__(self):
        return str(self.product) + " - " + str(self.quantity) + " - " + str(self.date)


class CarouselImage(models.Model):
    name = models.CharField(max_length=30, blank=True)
    url = models.TextField(max_length=200)

    def __str__(self):
        return str(self.url)


class CodigosReestablecimiento(models.Model):
    idUsuario = models.ForeignKey(
        MyUser, related_name="usuarios_set", on_delete=models.CASCADE
    )
    codigo = models.CharField(max_length=4)
    tiempoCreacion = models.DateTimeField()
    isUtilizado = models.BooleanField(default=False)
    
class Service(models.Model):
    name = models.CharField(max_length=30)
    categoria = models.ForeignKey(CategoriesService, on_delete=models.CASCADE)
    description = models.CharField(max_length=70)
    url = models.TextField(max_length=200, blank=True)
    
    def __str__(self):
        return str(self.name)

class Carrito(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Carrito de {self.usuario.email}"

    def get_precio_total(self):
        return sum(item.get_precio_total() for item in self.items.all())

    def limpiar(self):
        self.items.all().delete()        

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('Product', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.detail}"

    def get_precio_total(self):
        return self.cantidad * self.producto.price


class Orden(models.Model):
    ESTADOS_ORDEN = [
        ('Enviada', 'Enviada'),
        ('Completada', 'Completada'),
        ('Eliminada', 'Eliminada'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    precio_total = models.FloatField()
    estado = models.CharField(max_length=10, choices=ESTADOS_ORDEN, default='Enviada')

    def __str__(self):
        return f"Orden #{self.id} por {self.usuario.email} - {self.get_estado_display()}"

    def get_precio_total(self):
        return sum(item.get_precio_total() for item in self.items.all())

class DetalleOrden(models.Model):
    orden = models.ForeignKey(Orden, related_name='items', on_delete=models.CASCADE)
    producto = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio = models.FloatField()  # Precio en el momento de la compra

    def __str__(self):
        return f"{self.cantidad} x {self.producto.detail} @ {self.precio} cada uno"

    @property
    def get_precio_total(self):
        return self.cantidad * self.precio
    
class Comentario(models.Model):
    usuario = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    producto = models.ForeignKey('Product', on_delete=models.CASCADE)
    comentario = models.TextField()
    puntuacion = models.PositiveSmallIntegerField(default=5)  # De 1 a 5
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'producto')  # Un usuario solo puede comentar una vez por producto

    def __str__(self):
        return f"Comentario de {self.usuario.email} en {self.producto.detail} con puntuación {self.puntuacion}"