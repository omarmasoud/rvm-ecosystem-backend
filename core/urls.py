from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# create router for viewsets
router = DefaultRouter()
router.register(r'materials', views.MaterialTypeViewSet, basename='material')
router.register(r'rvms', views.RVMViewSet, basename='rvm')
router.register(r'activities', views.RecyclingActivityViewSet, basename='activity')

# admin router
admin_router = DefaultRouter()
admin_router.register(r'users', views.AdminUserViewSet, basename='admin-user')
admin_router.register(r'rvms', views.AdminRVMViewSet, basename='admin-rvm')
admin_router.register(r'activities', views.AdminRecyclingActivityViewSet, basename='admin-activity')
admin_router.register(r'materials', views.AdminMaterialTypeViewSet, basename='admin-material')
admin_router.register(r'wallets', views.AdminRewardWalletViewSet, basename='admin-wallet')

app_name = 'core'

urlpatterns = [
    path('', views.CustomAPIRoot.as_view(), name='api-root'), # Custom API root
    # authentication
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.CustomAuthToken.as_view(), name='login'),
    
    # user endpoints
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('summary/', views.user_summary, name='summary'),
    path('wallet/', views.RewardWalletView.as_view(), name='wallet'),
    
    # main functionality
    path('deposit/', views.DepositRecyclablesView.as_view(), name='deposit'),
    
    # viewset endpoints included under this root
    path('', include(router.urls)),
    
    # admin endpoints included under this root
    path('admin/', include(admin_router.urls)),
] 