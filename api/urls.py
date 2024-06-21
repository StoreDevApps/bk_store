from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutAndBlacklistRefreshTokenForUserView.as_view(), name='token_blacklist'),
    path('products-without-login/', views.ListOfProductsWithoutLoginView.as_view(), name='products_list'),
    path('contactus/', views.emailContactUs.as_view(), name='contactus'),
]