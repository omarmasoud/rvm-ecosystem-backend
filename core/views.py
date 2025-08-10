from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.shortcuts import redirect

from .models import User, UserRole, MaterialType, RVM, RewardWallet, RewardTransaction, RecyclingActivity
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    MaterialTypeSerializer, RVMSerializer, RewardWalletSerializer,
    RewardTransactionSerializer, RecyclingActivitySerializer,
    RecyclingActivityCreateSerializer, UserSummarySerializer
)


def home(request):
    """Root view: redirect based on authentication status"""
    if request.user.is_authenticated:
        return redirect('/admin/')
    return redirect('/admin/login/')


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
        
        return summary


class MaterialTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve material types"""
    queryset = MaterialType.objects.filter(is_active=True)
    serializer_class = MaterialTypeSerializer
    permission_classes = [IsAuthenticated]


class RVMViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve RVMs"""
    serializer_class = RVMSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = RVM.objects.all()
        
        # filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # filter by recent activity (last 24h)
        recent_only = self.request.query_params.get('recent', None)
        if recent_only:
            yesterday = datetime.now() - timedelta(days=1)
            queryset = queryset.filter(last_usage__gte=yesterday)
        
        # filter by location
        location = self.request.query_params.get('location', None)
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset.order_by('-last_usage')


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deposit_recyclables(request):
    """Main deposit endpoint - logs recycling and awards points"""
    serializer = RecyclingActivityCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        activity = serializer.save()
        
        return Response({
            'message': 'Deposit recorded successfully',
            'activity': RecyclingActivitySerializer(activity).data,
            'points_earned': float(activity.points_earned)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
