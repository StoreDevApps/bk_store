from django.conf import settings
from django.template.loader import get_template
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.models import (    
    CategoriesService,
    CodigosReestablecimiento,
    MyUser,
    Product,
    ProductHistory,
    ProductCategory,
    Rol,
    Service,
)

from django.db.models import OuterRef, Subquery, FloatField
from django.db.models.functions import Cast
from rest_framework.views import APIView

from api.serializers import ProductSerializer

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = MyUser.objects.get(id=user_id)
            return Response({
                "name": user.name,
                "last_name": user.last_name,
                "email": user.email,
                "role": user.rol.user_type if user.rol else None,
            })
        except MyUser.DoesNotExist:
            return Response({"error": "User not found"}, status=404)


class ProductDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

class ProductPaginationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        offset = (page - 1) * page_size

        categories = request.GET.get('categories', '')
        categories_list = categories.split(',') if categories else []

        min_price = request.GET.get('minPrice', '').strip() or None
        max_price = request.GET.get('maxPrice', '').strip() or None
        search_query = request.GET.get('searchQuery', '').strip().lower() or None

        sort_option = request.GET.get('sortOption')

        # Imprimir los filtros recibidos
        print("Filtros recibidos:")
        print(f"Categorías: {categories_list}")
        print(f"Min Price: {min_price}")
        print(f"Max Price: {max_price}")
        print(f"Search Query: '{search_query}'")
        print(f"Sort Option: {sort_option}")

        # Subconsulta para obtener el precio más reciente
        latest_price_subquery = ProductHistory.objects.filter(
            product=OuterRef('pk')
        ).order_by('-date').values('unit_sales_price')[:1]

        # Obtener todos los productos
        products = Product.objects.all()

        # Aplicar los filtros de categorías
        if categories_list:
            products = products.filter(category__id__in=categories_list)

        filtered_products = []

        for product in products:
            # Obtener el precio más reciente para cada producto
            latest_price = ProductHistory.objects.filter(product=product).order_by('-date').values_list('unit_sales_price', flat=True).first()

            # Imprimir el precio más reciente
            print(f"Producto: {product.detail}, Precio más reciente: {latest_price}")

            # Filtrado manual por precio
            if latest_price is not None:
                if min_price and latest_price < float(min_price):
                    print(f"Excluido por precio menor que min_price: {product.detail}")
                    continue
                if max_price and latest_price > float(max_price):
                    print(f"Excluido por precio mayor que max_price: {product.detail}")
                    continue

            # Filtrar por búsqueda
            if search_query and search_query not in product.detail.lower():
                print(f"Excluido por no coincidir con searchQuery: {product.detail}")
                continue

            # Añadir producto al listado filtrado
            filtered_products.append(product)

        # Imprimir los productos filtrados
        print("Productos filtrados manualmente:")
        for product in filtered_products:
            latest_price = ProductHistory.objects.filter(product=product).order_by('-date').values_list('unit_sales_price', flat=True).first()
            print(f"Producto: {product.detail}, Precio: {latest_price}")

        # Ordenar productos manualmente
        if sort_option:
            if sort_option == 'price-asc':
                filtered_products.sort(key=lambda x: float(ProductHistory.objects.filter(product=x).order_by('-date').values_list('unit_sales_price', flat=True).first() or 0))
            elif sort_option == 'price-desc':
                filtered_products.sort(key=lambda x: float(ProductHistory.objects.filter(product=x).order_by('-date').values_list('unit_sales_price', flat=True).first() or 0), reverse=True)
            elif sort_option == 'name-asc':
                filtered_products.sort(key=lambda x: x.detail.lower())
            elif sort_option == 'name-desc':
                filtered_products.sort(key=lambda x: x.detail.lower(), reverse=True)

        total_products = len(filtered_products)
        paginated_products = filtered_products[offset:offset + page_size]

        products_list = [product.to_json() for product in paginated_products]

        return Response(
            {
                "success": True,
                "products": products_list,
                "total_pages": (total_products + page_size - 1) // page_size
            },
            status=status.HTTP_200_OK
        )

    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        offset = (page - 1) * page_size

        categories = request.GET.get('categories', '')
        categories_list = categories.split(',') if categories else []

        min_price = request.GET.get('minPrice')
        max_price = request.GET.get('maxPrice')

        search_query = request.GET.get('searchQuery', '').strip().lower()

        sort_option = request.GET.get('sortOption')

        # Imprimir los filtros recibidos
        print("Filtros recibidos:")
        print(f"Categorías: {categories_list}")
        print(f"Min Price: {min_price}")
        print(f"Max Price: {max_price}")
        print(f"Search Query: '{search_query}'")
        print(f"Sort Option: {sort_option}")

        # Subconsulta para obtener el precio más reciente
        latest_price_subquery = ProductHistory.objects.filter(
            product=OuterRef('pk')
        ).order_by('-date').values('unit_sales_price')[:1]

        # Obtener todos los productos
        products = Product.objects.all()

        # Aplicar los filtros de categorías
        if categories_list:
            products = products.filter(category__id__in=categories_list)

        filtered_products = []

        for product in products:
            # Obtener el precio más reciente para cada producto
            latest_price = ProductHistory.objects.filter(product=product).order_by('-date').values_list('unit_sales_price', flat=True).first()

            # Imprimir el precio más reciente
            print(f"Producto: {product.detail}, Precio más reciente: {latest_price}")

            # Filtrado manual por precio
            if latest_price is not None:
                if min_price and float(latest_price) < float(min_price):
                    print(f"Excluido por precio menor que min_price: {product.detail}")
                    continue
                if max_price and float(latest_price) > float(max_price):
                    print(f"Excluido por precio mayor que max_price: {product.detail}")
                    continue

            # Filtrar por búsqueda
            if search_query and search_query not in product.detail.lower():
                print(f"Excluido por no coincidir con searchQuery: {product.detail}")
                continue

            # Añadir producto al listado filtrado
            filtered_products.append(product)

        # Imprimir los productos filtrados
        print("Productos filtrados manualmente:")
        for product in filtered_products:
            latest_price = ProductHistory.objects.filter(product=product).order_by('-date').values_list('unit_sales_price', flat=True).first()
            print(f"Producto: {product.detail}, Precio: {latest_price}")

        # Ordenar productos manualmente
        if sort_option:
            if sort_option == 'price-asc':
                filtered_products.sort(key=lambda x: float(ProductHistory.objects.filter(product=x).order_by('-date').values_list('unit_sales_price', flat=True).first() or 0))
            elif sort_option == 'price-desc':
                filtered_products.sort(key=lambda x: float(ProductHistory.objects.filter(product=x).order_by('-date').values_list('unit_sales_price', flat=True).first() or 0), reverse=True)
            elif sort_option == 'name-asc':
                filtered_products.sort(key=lambda x: x.detail.lower())
            elif sort_option == 'name-desc':
                filtered_products.sort(key=lambda x: x.detail.lower(), reverse=True)

        total_products = len(filtered_products)
        paginated_products = filtered_products[offset:offset + page_size]

        products_list = [product.to_json() for product in paginated_products]

        return Response(
            {
                "success": True,
                "products": products_list,
                "total_pages": (total_products + page_size - 1) // page_size
            },
            status=status.HTTP_200_OK
        )

