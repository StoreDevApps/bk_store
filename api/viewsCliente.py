from django.conf import settings
from django.template.loader import get_template
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView


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

from django.db.models import OuterRef, Subquery, Q

class ProductPaginationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        offset = (page - 1) * page_size

        categories = request.GET.get('categories', '')
        categories_list = categories.split(',') if categories else []

        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')

        # Subconsulta para obtener el precio más reciente
        latest_price_subquery = ProductHistory.objects.filter(
            product=OuterRef('pk')
        ).order_by('-date').values('unit_sales_price')[:1]

        # Construcción de la consulta de filtrado
        filter_query = Q(state='A')

        if categories_list:
            filter_query &= Q(category__id__in=categories_list)

        if min_price:
            filter_query &= Q(id__in=Product.objects.annotate(
                latest_price=Subquery(latest_price_subquery)
            ).filter(latest_price__gte=float(min_price)).values('id'))

        if max_price:
            filter_query &= Q(id__in=Product.objects.annotate(
                latest_price=Subquery(latest_price_subquery)
            ).filter(latest_price__lte=float(max_price)).values('id'))

        products = Product.objects.filter(filter_query)[offset:offset + page_size]
        total_products = Product.objects.filter(filter_query).count()
        total_pages = (total_products + page_size - 1) // page_size

        products_list = [product.to_json() for product in products]

        return Response(
            {
                "success": True,
                "products": products_list,
                "total_pages": total_pages
            },
            status=status.HTTP_200_OK
        )
