from django.conf import settings
from django.template.loader import get_template
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.models import (    
    CategoriesService,
    Comentario,
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
from .serializers import ComentarioSerializer
from django.shortcuts import get_object_or_404

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
 
class ProductCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        
        # Verificar si el usuario ha comentado el producto
        user_comment = Comentario.objects.filter(producto=product, usuario=request.user).first()
        user_has_commented = user_comment is not None

        # Obtener todos los comentarios excepto el del usuario actual
        comments = Comentario.objects.filter(producto=product).exclude(usuario=request.user)
        comments_data = [
            {
                "user_name": f"{comment.usuario.name} {comment.usuario.last_name}".strip() if comment.usuario.name else "Usuario sin nombre",
                "rating": comment.puntuacion,
                "comment": comment.comentario,
                "createdAt": comment.fecha_creacion,
                "updatedAt": comment.fecha_actualizacion if comment.fecha_actualizacion != comment.fecha_creacion else None
            } for comment in comments
        ]
        
        # Estructurar la respuesta
        response_data = {
            "comments": comments_data,
            "user_has_commented": user_has_commented,
            "user_comment": {
                "name": f"{request.user.name} {request.user.last_name}".strip(),
                "rating": user_comment.puntuacion,
                "comment": user_comment.comentario,
                "createdAt": user_comment.fecha_creacion,
                "updatedAt": user_comment.fecha_actualizacion if user_comment.fecha_actualizacion != user_comment.fecha_creacion else None
            } if user_has_commented else None
        }

        return Response(response_data)


class SubmitCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        user = request.user

        # Verificar si el usuario ha comprado el producto
        if not product.user_has_purchased(user):
            return Response({"error": "No puedes comentar porque no has comprado este producto."}, status=403)

        # Verificar si el usuario ya ha comentado
        if Comentario.objects.filter(producto=product, usuario=user).exists():
            return Response({"error": "Ya has comentado este producto."}, status=400)

        # Crear el comentario y la puntuación
        comentario_text = request.data.get('comment')
        puntuacion_valor = request.data.get('rating')

        if not comentario_text or not puntuacion_valor:
            return Response({"error": "Debe proporcionar tanto comentario como puntuación."}, status=400)

        Comentario.objects.create(
            usuario=user,
            producto=product,
            comentario=comentario_text,
            puntuacion=puntuacion_valor
        )

        return Response({"success": "Comentario y puntuación creados correctamente."}, status=201)



class UpdateCommentView(APIView):
    def put(self, request, product_id):
        user = request.user
        comentario = get_object_or_404(Comentario, producto_id=product_id, usuario=user)

        serializer = ComentarioSerializer(comentario, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print(serializer.data)  # Verifica qué datos se están guardando
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HasPurchasedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, product_id):
        user = request.user
        product = get_object_or_404(Product, id=product_id)
        has_purchased = product.user_has_purchased(user)
        return Response({"has_purchased": has_purchased})

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

