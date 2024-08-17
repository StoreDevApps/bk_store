from django.test import TestCase
from api.models import (
    Rol, MyUser, ProductCategory, CategoriesService, Suplier, Product, ProductImage,
    ProductVideo, ProductHistory, Inventory, Sale, CarouselImage, CodigosReestablecimiento,
    Service, Carrito, ItemCarrito, Orden, DetalleOrden, Comentario
)
from django.utils import timezone


class RolModelTest(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(user_type="Admin")

    def test_rol_str(self):
        self.assertEqual(str(self.rol), "Admin")


class MyUserModelTest(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(user_type="User")
        self.user = MyUser.objects.create_user(
            email="test@example.com",
            password="password123",
            name="Test",
            last_name="User",
            phone_number="1234567890",
            rol=self.rol
        )

    def test_user_str(self):
        self.assertEqual(str(self.user), "test@example.com")

    def test_user_to_json(self):
        user_json = self.user.to_json()
        self.assertEqual(user_json["name"], "Test")
        self.assertEqual(user_json["email"], "test@example.com")


class ProductCategoryModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="Electronics")

    def test_product_category_str(self):
        self.assertEqual(str(self.category), "Electronics")


class CategoriesServiceModelTest(TestCase):
    def setUp(self):
        self.category = CategoriesService.objects.create(name="Maintenance")

    def test_categories_service_str(self):
        self.assertEqual(str(self.category), "Maintenance")


class SuplierModelTest(TestCase):
    def setUp(self):
        self.suplier = Suplier.objects.create(name="Supplier A", email="supplier@example.com")

    def test_suplier_str(self):
        self.assertEqual(str(self.suplier), "Supplier A")


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="Category")
        self.product = Product.objects.create(
            presentation="Test Presentation",
            category=self.category,
            detail="Test Product",
            brand="Test Brand",
            codigo="12345",
            duedate=timezone.now(),
            units=10
        )

    def test_product_str(self):
        self.assertEqual(str(self.product), "Test Product (Test Brand)")

    def test_product_to_json(self):
        json_data = self.product.to_json()
        self.assertIn("presentation", json_data)
        self.assertIn("detail", json_data)
        self.assertIn("brand", json_data)
        self.assertEqual(json_data["detail"], "Test Product")


class ProductImageModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="Category")
        self.product = Product.objects.create(
            presentation="Test Presentation",
            category=self.category,
            detail="Test Product",
            brand="Test Brand",
            codigo="12345",
            duedate=timezone.now(),
            units=10
        )
        self.product_image = ProductImage.objects.create(
            product=self.product, url="http://example.com/image.png"
        )

    def test_product_image_str(self):
        self.assertEqual(str(self.product_image), "http://example.com/image.png")


class ProductVideoModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="Category")
        self.product = Product.objects.create(
            presentation="Test Presentation",
            category=self.category,
            detail="Test Product",
            brand="Test Brand",
            codigo="12345",
            duedate=timezone.now(),
            units=10
        )
        self.product_video = ProductVideo.objects.create(
            product=self.product, url="http://example.com/video.mp4"
        )

    def test_product_video_str(self):
        self.assertEqual(str(self.product_video), "http://example.com/video.mp4")


class ProductHistoryModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="Category")
        self.suplier = Suplier.objects.create(name="Supplier A", email="supplier@example.com")
        self.product = Product.objects.create(
            presentation="Test Presentation",
            category=self.category,
            detail="Test Product",
            brand="Test Brand",
            codigo="12345",
            duedate=timezone.now(),
            units=10
        )
        self.product_history = ProductHistory.objects.create(
            date=timezone.now(),
            product=self.product,
            suplier=self.suplier,
            unit_cost_price=10.0,
            unit_sales_price=15.0,
            units_purchased=100
        )

    def test_product_history_str(self):
        self.assertEqual(
            str(self.product_history),
            f"{self.product} - {self.suplier} - {self.product_history.date}"
        )


class InventoryModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="Category")
        self.product = Product.objects.create(
            presentation="Test Presentation",
            category=self.category,
            detail="Test Product",
            brand="Test Brand",
            codigo="12345",
            duedate=timezone.now(),
            units=10
        )
        self.inventory = Inventory.objects.create(
            product=self.product, quantity=50, sales_price=20.0
        )

    def test_inventory_str(self):
        self.assertEqual(
            str(self.inventory),
            f"{self.product} - {self.inventory.quantity} - {self.inventory.sales_price}"
        )


class SaleModelTest(TestCase):
    def setUp(self):
        self.category = ProductCategory.objects.create(name="Category")
        self.product = Product.objects.create(
            presentation="Test Presentation",
            category=self.category,
            detail="Test Product",
            brand="Test Brand",
            codigo="12345",
            duedate=timezone.now(),
            units=10
        )
        self.sale = Sale.objects.create(
            product=self.product, quantity=5, date=timezone.now()
        )

    def test_sale_str(self):
        self.assertEqual(
            str(self.sale),
            f"{self.sale.product} - {self.sale.quantity} - {self.sale.date}"
        )


class CarouselImageModelTest(TestCase):
    def setUp(self):
        self.carousel_image = CarouselImage.objects.create(
            name="Image 1",
            url="http://example.com/image1.png"
        )

    def test_carousel_image_str(self):
        self.assertEqual(str(self.carousel_image), "http://example.com/image1.png")


class CodigosReestablecimientoModelTest(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(user_type="User")
        self.user = MyUser.objects.create_user(
            email="test@example.com",
            password="password123",
            name="Test",
            last_name="User",
            phone_number="1234567890",
            rol=self.rol
        )
        self.codigo_reestablecimiento = CodigosReestablecimiento.objects.create(
            idUsuario=self.user, codigo="1234", tiempoCreacion=timezone.now(), isUtilizado=False
        )

    def test_codigos_reestablecimiento(self):
        self.assertEqual(str(self.codigo_reestablecimiento.codigo), "1234")


class ServiceModelTest(TestCase):
    def setUp(self):
        self.category = CategoriesService.objects.create(name="Maintenance")
        self.service = Service.objects.create(
            name="Service 1", categoria=self.category, description="Service description"
        )

    def test_service_str(self):
        self.assertEqual(str(self.service), "Service 1")


class CarritoModelTest(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(user_type="User")
        self.user = MyUser.objects.create_user(
            email="test@example.com",
            password="password123",
            name="Test",
            last_name="User",
            phone_number="1234567890",
            rol=self.rol
        )
        self.carrito = Carrito.objects.create(usuario=self.user)

    def test_carrito_str(self):
        self.assertEqual(str(self.carrito), f"Carrito de {self.user.email}")

    def test_get_precio_total(self):
        category = ProductCategory.objects.create(name="Category")
        product = Product.objects.create(
            presentation="Test Presentation",
            category=category,
            detail="Test Product",
            brand="Test Brand",
            codigo="12345",
            duedate=timezone.now(),
            units=10
        )
        ProductHistory.objects.create(
            product=product,
            suplier=Suplier.objects.create(name="Suplier A"),
            date=timezone.now(),
            unit_cost_price=10.0,
            unit_sales_price=50.0,
            units_purchased=100
        )
        ItemCarrito.objects.create(
            carrito=self.carrito, producto=product, cantidad=2
        )
        self.assertEqual(self.carrito.get_precio_total(), 100.0)


class OrdenModelTest(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(user_type="User")
        self.user = MyUser.objects.create_user(
            email="test@example.com",
            password="password123",
            name="Test",
            last_name="User",
            phone_number="1234567890",
            rol=self.rol
        )
        self.orden = Orden.objects.create(
            usuario=self.user, precio_total=200.0, estado="Creando"
        )

    def test_orden_str(self):
        self.assertEqual(
            str(self.orden).replace("\n", "").replace(" ", ""),
            f"Orden#{self.orden.id}por{self.user.email}-Creando"
        )


class DetalleOrdenModelTest(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(user_type="User")
        self.user = MyUser.objects.create_user(
            email="test@example.com",
            password="password123",
            name="Test",
            last_name="User",
            phone_number="1234567890",
            rol=self.rol
        )
        self.category = ProductCategory.objects.create(name="Category")
        self.product = Product.objects.create(
            presentation="Test Presentation",
            category=self.category,
            detail="Test Product",
            brand="Test Brand",
            codigo="12345",
            duedate=timezone.now(),
            units=10
        )
        self.orden = Orden.objects.create(
            usuario=self.user, precio_total=200.0, estado="Creando"
        )
        self.detalle_orden = DetalleOrden.objects.create(
            orden=self.orden, producto=self.product, cantidad=3, precio=50.0
        )

    def test_detalle_orden_str(self):
        self.assertEqual(
            str(self.detalle_orden).replace("\n", "").replace(" ", ""),
            (
                f"{self.detalle_orden.cantidad}x"
                f"{self.product.detail.replace(' ', '')}@"
                f"{self.detalle_orden.precio}cadauno"
            )
        )

    def test_get_precio_total(self):
        self.assertEqual(self.detalle_orden.get_precio_total, 150.0)


class ComentarioModelTest(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(user_type="User")
        self.user = MyUser.objects.create_user(
            email="test@example.com",
            password="password123",
            name="Test",
            last_name="User",
            phone_number="1234567890",
            rol=self.rol
        )
        self.category = ProductCategory.objects.create(name="Category")
        self.product = Product.objects.create(
            presentation="Test Presentation",
            category=self.category,
            detail="Test Product",
            brand="Test Brand",
            codigo="12345",
            duedate=timezone.now(),
            units=10
        )
        self.comentario = Comentario.objects.create(
            usuario=self.user, producto=self.product, comentario="Great product!", puntuacion=5
        )

    def test_comentario_str(self):
        self.assertEqual(
            str(self.comentario).replace("\n", "").replace(" ", ""),
            (
                f"Comentariode{self.user.email}en"
                f"{self.product.detail.replace(' ', '')}conpuntuación"
                f"{self.comentario.puntuacion}"
            )
        )
