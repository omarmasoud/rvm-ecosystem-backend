from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserRole, MaterialType, RVM, RewardWallet, RewardTransaction, RecyclingActivity


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'name', 'description']


class UserSerializer(serializers.ModelSerializer):
    """Main user serializer - excludes sensitive fields"""
    role = UserRoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'role', 'role_id', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Simple login serializer"""
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs


class MaterialTypeSerializer(serializers.ModelSerializer):
    """Serializer for recyclable material types and their point values"""
    class Meta:
        model = MaterialType
        fields = ['id', 'name', 'points_per_kg', 'is_active']


class RVMSerializer(serializers.ModelSerializer):
    """Serializer for RVMs, used in discovery API. Includes activity count."""
    activity_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RVM
        fields = ['id', 'name', 'location', 'status', 'last_usage', 'activity_count']
        read_only_fields = ['id', 'last_usage', 'activity_count']
    
    def get_activity_count(self, obj):
        return obj.recyclingactivity_set.count()


class RewardWalletSerializer(serializers.ModelSerializer):
    """User's wallet with transaction history"""
    user = UserSerializer(read_only=True)
    recent_transactions = serializers.SerializerMethodField()
    
    class Meta:
        model = RewardWallet
        fields = ['user', 'points', 'credit', 'recent_transactions']
        read_only_fields = ['user', 'points', 'credit']
    
    def get_recent_transactions(self, obj):
        """Get last 5 transactions"""
        transactions = obj.rewardtransaction_set.all()[:5]
        return RewardTransactionSerializer(transactions, many=True).data


class RewardTransactionSerializer(serializers.ModelSerializer):
    """Transaction history serializer"""
    wallet = RewardWalletSerializer(read_only=True)
    
    class Meta:
        model = RewardTransaction
        fields = ['id', 'wallet', 'change_amount', 'reason', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class RecyclingActivitySerializer(serializers.ModelSerializer):
    """Main recycling activity serializer"""
    user = UserSerializer(read_only=True)
    rvm = RVMSerializer(read_only=True)
    material = MaterialTypeSerializer(read_only=True)
    
    class Meta:
        model = RecyclingActivity
        fields = ['id', 'user', 'rvm', 'material', 'weight', 'points_earned', 'timestamp']
        read_only_fields = ['id', 'user', 'points_earned', 'timestamp']


class RecyclingActivityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new recycling activities"""
    rvm_id = serializers.IntegerField(write_only=True)
    material_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = RecyclingActivity
        fields = ['rvm_id', 'material_id', 'weight']
    
    def validate_rvm_id(self, value):
        """Check if RVM exists and is active"""
        try:
            rvm = RVM.objects.get(id=value)
            if rvm.status != 'active':
                raise serializers.ValidationError("RVM is not active")
            return value
        except RVM.DoesNotExist:
            raise serializers.ValidationError("RVM not found")
    
    def validate_material_id(self, value):
        """Check if material exists and is active"""
        try:
            material = MaterialType.objects.get(id=value, is_active=True)
            return value
        except MaterialType.DoesNotExist:
            raise serializers.ValidationError("Material not found or inactive")
    
    def create(self, validated_data):
        # extract the IDs and set the actual objects
        rvm_id = validated_data.pop('rvm_id')
        material_id = validated_data.pop('material_id')
        
        validated_data['rvm'] = RVM.objects.get(id=rvm_id)
        validated_data['material'] = MaterialType.objects.get(id=material_id)
        validated_data['user'] = self.context['request'].user
        
        return super().create(validated_data)


class UserSummarySerializer(serializers.Serializer):
    """Serializer for user summary stats"""
    total_recycled_weight = serializers.FloatField()
    total_points_earned = serializers.FloatField()
    deposits_count = serializers.IntegerField()
    member_since = serializers.CharField()
    current_points = serializers.FloatField()
    current_credit = serializers.FloatField() 