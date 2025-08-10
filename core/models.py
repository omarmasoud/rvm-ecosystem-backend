from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class UserRole(models.Model):
    """Different user types in the system - regular users, admins, technicians"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        # gotta keep it organized
        ordering = ['name']


class User(AbstractUser):
    """Custom user model - extends Django's built-in user"""
    # override username to use email instead
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=15, 
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number')],
        blank=True
    )
    role = models.ForeignKey(UserRole, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def summary(self):
        """Get user's recycling stats - used in Task 3 requirements"""
        total_weight = sum(activity.weight for activity in self.recyclingactivity_set.all())
        total_points = sum(activity.points_earned for activity in self.recyclingactivity_set.all())
        
        return {
            'total_recycled_weight': float(total_weight),
            'total_points_earned': float(total_points),
            'deposits_count': self.recyclingactivity_set.count(),
            'member_since': self.created_at.strftime('%Y-%m-%d')
        }


class MaterialType(models.Model):
    """Different types of recyclable materials and their point values"""
    name = models.CharField(max_length=100, unique=True)  # Plastic, Glass, Metal, etc.
    points_per_kg = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.points_per_kg} pts/kg)"
    
    class Meta:
        ordering = ['name']


class RVM(models.Model):
    """Recycling Vending Machine - the actual hardware"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    name = models.CharField(max_length=100, blank=True)  # optional identifier
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_usage = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        if self.name:
            return f"{self.name} - {self.location}"
        return f"RVM {self.id} - {self.location}"
    
    class Meta:
        # order by most recently used
        ordering = ['-last_usage']


class RewardWallet(models.Model):
    """User's current point and credit balance"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.user.email}'s wallet - {self.points} pts, ${self.credit}"
    
    def add_points(self, amount, reason="deposit"):
        """Add points and create transaction record"""
        self.points += amount
        self.save()
        
        # create transaction record
        RewardTransaction.objects.create(
            wallet=self,
            change_amount=amount,
            reason=reason
        )


class RewardTransaction(models.Model):
    """Track all changes to user wallets - audit trail"""
    wallet = models.ForeignKey(RewardWallet, on_delete=models.CASCADE)
    change_amount = models.DecimalField(max_digits=10, decimal_places=2)  # can be negative
    reason = models.CharField(max_length=100)  # deposit, redemption, adjustment, etc.
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.wallet.user.email} - {self.change_amount} ({self.reason})"
    
    class Meta:
        ordering = ['-timestamp']


class RecyclingActivity(models.Model):
    """Record of each recycling transaction"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rvm = models.ForeignKey(RVM, on_delete=models.CASCADE)
    material = models.ForeignKey(MaterialType, on_delete=models.PROTECT)
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=3,
        validators=[MinValueValidator(Decimal('0.001'))]  # minimum 1 gram
    )
    points_earned = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.weight}kg {self.material.name} at RVM {self.rvm.id}"
    
    def save(self, *args, **kwargs):
        # auto-calculate points if not set
        if not self.points_earned:
            self.points_earned = self.weight * self.material.points_per_kg
        
        # update RVM last usage
        self.rvm.last_usage = self.timestamp
        self.rvm.save()
        
        # add points to user's wallet
        wallet, created = RewardWallet.objects.get_or_create(user=self.user)
        wallet.add_points(self.points_earned, f"recycling_{self.material.name.lower()}")
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Recycling activities"  # looks better in admin
