from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
import os

from api import viewsCliente
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("token/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("enviarCodigo/", views.EnviarCodigo.as_view()),
    path("verificarCodigo/", views.VerificarCodigo.as_view()),
    path("reestablecerContra/", views.ReestablecerContrasena.as_view()),
    path(
        "logout/",
        views.LogoutAndBlacklistRefreshTokenForUserView.as_view(),
        name="token_blacklist",
    ),
    path(
        "products-without-login/",
        views.ListOfProductsWithoutLoginView.as_view(),
        name="products_list",
    ),
    path("contactus/", views.EmailContactUs.as_view(), name="contactus"),
    path(
        "product-categories/",
        views.ListOfProductCategoryView.as_view(),
        name="list_products_category",
    ),
    path(
        "product-category/<int:pk>/",
        views.ProductCategoryView.as_view(),
        name="products_list",
    ),
    path("products-pagination/", viewsCliente.ProductPaginationView.as_view(), name="products_pagination"),

    path("products/", views.ListOfProductsView.as_view(), name="products_list"),
    path('product/<int:product_id>/multimedia/', views.GetMultimediaProductoView.as_view(), name='get_multimedia_producto'),
    path(
        "public/carousel-home/",
        views.CarouselImageHomeView.as_view(),
        name="carousel_home",
    ),
    path('services/', views.PublicServicesView.as_view(), name="public_services"),
    path('admin/categories-services/', views.AdminCategoriesServicesView.as_view(), name="admin_categories_services"),
    path('admin/carousel-images/', views.UploadCarouselImageView.as_view(), name="carousel_image"),
    path('admin/carousel-image/<int:pk>/', views.DeleteCarouselImageView.as_view(), name="delete_carousel_image"),
    path('admin/services/', views.AdminServicesView.as_view(), name="admin_services"),
    path('admin/service/<int:pk>/', views.AdminServiceView.as_view(), name="admin_service"),
    path('admin/list-workers/', views.UserWorkerListView.as_view(), name="admin_list_workers"),
    path('admin/worker-to-admin/', views.WorkerToAdminView.as_view(), name="worker_to_admin"),
    
    path('user/<int:user_id>/', viewsCliente.UserDetailView.as_view(), name='user_detail'),
    
    path('admin/products/', views.ListadoProductosView.as_view(), name="admin_products"),
    path('admin/product-images/', views.ImagenesProductoView.as_view(), name="admin_product_images"),
    path('products/<int:product_id>/images/', views.DeleteProductImageView.as_view(), name='delete-product-image'),

    path('products/<int:product_id>/', viewsCliente.ProductDetailView.as_view(), name='product-detail'),
    path('products/<int:product_id>/comments/', viewsCliente.ProductCommentsView.as_view(), name='product-comments'),
    path('products/<int:product_id>/comments/submit', viewsCliente.SubmitCommentView.as_view(), name='submit-comment'),
    path('products/<int:product_id>/has-purchased', viewsCliente.HasPurchasedView.as_view(), name='has-purchased'),
    path('products/<int:product_id>/comments/update', viewsCliente.UpdateCommentView.as_view(), name='update-comment'),

    path('carrito/item-count', viewsCliente.CartItemCountView.as_view(), name='cart-item-count'),
    path('carrito/items', viewsCliente.CartItemsView.as_view(), name='cart-items'),
    path('carrito/add', viewsCliente.AddToCartView.as_view(), name='add-to-cart'),
    path('carrito/clear', viewsCliente.ClearCartView.as_view(), name='clear-cart'),    
]

if settings.DEBUG:
    urlpatterns += static('/public/', document_root=os.path.join(settings.BASE_DIR, 'public'))