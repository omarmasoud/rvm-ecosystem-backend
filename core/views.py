from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.validators import MinValueValidator
from django_filters.rest_framework import DjangoFilterBackend
import django_filters

from rest_framework.response import Response # Import Response
from rest_framework.reverse import reverse # Import reverse
from rest_framework.views import APIView # Import APIView

from .models import User, UserRole, MaterialType, RVM, RewardWallet, RewardTransaction, RecyclingActivity
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    MaterialTypeSerializer, RVMSerializer, RewardWalletSerializer,
    RewardTransactionSerializer, RecyclingActivityCreateSerializer, UserSummarySerializer, RecyclingActivitySerializer
)


class CustomAPIRoot(APIView):
    """Custom API Root view to display all available endpoints."""
    permission_classes = [] # Allow unauthenticated access to the API root overview

    def get(self, request, format=None):
        return Response({
            'auth_register': reverse('core:register', request=request, format=format),
            'auth_login': reverse('core:login', request=request, format=format),
            'user_profile': reverse('core:profile', request=request, format=format),
            'user_summary': reverse('core:summary', request=request, format=format),
            'user_wallet': reverse('core:wallet', request=request, format=format),
            'deposit_recyclables': reverse('core:deposit', request=request, format=format),

            'materials': reverse('core:material-list', request=request, format=format),
            'rvms': reverse('core:rvm-list', request=request, format=format),
            'recycling_activities': reverse('core:activity-list', request=request, format=format),
            
            'admin_users': reverse('core:admin-user-list', request=request, format=format),
            'admin_rvms': reverse('core:admin-rvm-list', request=request, format=format),
            'admin_activities': reverse('core:admin-activity-list', request=request, format=format),
            'admin_materials': reverse('core:admin-material-list', request=request, format=format),
            'admin_wallets': reverse('core:admin-wallet-list', request=request, format=format),
        })


class UserRegistrationView(generics.CreateAPIView):
    """Register new users"""
    serializer_class = UserRegistrationSerializer
    permission_classes = []  # anyone can register
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # create token for immediate login
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'User registered successfully',
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class CustomAuthToken(ObtainAuthToken):
    """Custom login endpoint that returns user data too"""
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserSummaryView(generics.RetrieveAPIView):
    """Get user's recycling summary stats"""
    serializer_class = UserSummarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        summary = user.summary()
        
        # add current wallet info
        wallet, created = RewardWallet.objects.get_or_create(user=user)
        summary['current_points'] = float(wallet.points)
        summary['current_credit'] = float(wallet.credit)
        
        return Response(summary)


class MaterialTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve material types"""
    queryset = MaterialType.objects.filter(is_active=True)
    serializer_class = MaterialTypeSerializer
    permission_classes = [IsAuthenticated]


class RVMFilter(django_filters.FilterSet):
    id = django_filters.NumberFilter(field_name='id', lookup_expr='exact', validators=[MinValueValidator(0)]) # Filter by exact ID, must be 0 or greater
    name = django_filters.CharFilter(lookup_expr='icontains') # Filter by partial, case-insensitive name
    status = django_filters.ChoiceFilter(choices=RVM.STATUS_CHOICES, lookup_expr='exact') # Status as dropdown

    class Meta:
        model = RVM
        fields = ['id', 'name', 'status', 'location'] # Remove last_usage from fields


class RVMViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve RVMs with advanced filtering"""
    serializer_class = RVMSerializer
    permission_classes = [IsAuthenticated]
    queryset = RVM.objects.all().order_by('-last_usage') # Set initial queryset and ordering here
    filter_backends = [DjangoFilterBackend]
    filterset_class = RVMFilter


class RewardWalletView(generics.RetrieveAPIView):
    """Get user's wallet with transaction history"""
    serializer_class = RewardWalletSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        wallet, created = RewardWallet.objects.get_or_create(user=self.request.user)
        return wallet


class RecyclingActivityViewSet(viewsets.ModelViewSet):
    """CRUD operations for recycling activities"""
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return RecyclingActivityCreateSerializer
        return RecyclingActivitySerializer
    
    def get_queryset(self):
        # users can only see their own activities
        return RecyclingActivity.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create activity and automatically handle points"""
        activity = serializer.save()
        return activity


class DepositRecyclablesView(generics.CreateAPIView):
    """Main deposit endpoint - logs recycling and awards points"""
    serializer_class = RecyclingActivityCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # The serializer's create method already handles setting user, rvm, and material.
        # The save method of the RecyclingActivity model handles RVM last_usage update and points.
        activity = serializer.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_summary(request):
    """Get user's recycling summary - total weight and points"""
    user = request.user
    summary = user.summary()
    
    # add wallet info
    wallet, created = RewardWallet.objects.get_or_create(user=user)
    summary['current_points'] = float(wallet.points)
    summary['current_credit'] = float(wallet.credit)
    
    return Response(summary)


# Admin-only views
class AdminUserViewSet(viewsets.ModelViewSet):
    """Admin CRUD for users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class AdminRVMViewSet(viewsets.ModelViewSet):
    """Admin CRUD for RVMs"""
    queryset = RVM.objects.all()
    serializer_class = RVMSerializer
    permission_classes = [IsAdminUser]


class AdminRecyclingActivityViewSet(viewsets.ModelViewSet):
    """Admin CRUD for all recycling activities"""
    queryset = RecyclingActivity.objects.all()
    serializer_class = RecyclingActivitySerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = RecyclingActivity.objects.all()
        
        # filter by user
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # filter by RVM
        rvm_id = self.request.query_params.get('rvm', None)
        if rvm_id:
            queryset = queryset.filter(rvm_id=rvm_id)
        
        # filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(timestamp__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__date__lte=end_date)
        
        return queryset.order_by('-timestamp')


class AdminMaterialTypeViewSet(viewsets.ModelViewSet):
    """Admin CRUD for material types"""
    queryset = MaterialType.objects.all()
    serializer_class = MaterialTypeSerializer
    permission_classes = [IsAdminUser]


class AdminRewardWalletViewSet(viewsets.ModelViewSet):
    """Admin CRUD for reward wallets"""
    queryset = RewardWallet.objects.all()
    serializer_class = RewardWalletSerializer
    permission_classes = [IsAdminUser]