from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
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
]
