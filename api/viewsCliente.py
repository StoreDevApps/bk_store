import base64
import json
import os
import random
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
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView


from api.models import (    
    CategoriesService,
    CodigosReestablecimiento,
    MyUser,
    Product,
    ProductCategory,
    Rol,
    Service,
)

class ProductPaginationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        offset = (page - 1) * page_size

        products = Product.objects.filter(state='A')[offset:offset + page_size]
        total_products = Product.objects.filter(state='A').count()
        total_pages = (total_products + page_size - 1) // page_size

        # Use the to_json method of the Product model
        products_list = [product.to_json() for product in products]

        return Response(
            {
                "success": True, 
                "products": products_list, 
                "total_pages": total_pages
            }, 
            status=status.HTTP_200_OK
        )
