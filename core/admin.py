from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, UserRole, MaterialType, RVM, RewardWallet, RewardTransaction, RecyclingActivity


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'phone', 'role', 'created_at', 'is_active']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']
    
    # customize fieldsets for our custom fields
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(MaterialType)
class MaterialTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_per_kg', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['name']


@admin.register(RVM)
class RVMAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'location', 'status', 'last_usage', 'activity_count']
    list_filter = ['status', 'last_usage']
    search_fields = ['name', 'location']
    ordering = ['-last_usage']
    list_editable = ['status']  # Allow editing status directly in list
    list_display_links = ['id', 'name']  # Make both ID and name clickable
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'location', 'status')
        }),
        ('Usage Info', {
            'fields': ('last_usage',),
            'classes': ('collapse',)
        }),
    )
    
    def activity_count(self, obj):
        """Show how many recycling activities this RVM has"""
        count = obj.recyclingactivity_set.count()
        return count
    activity_count.short_description = 'Activities'


@admin.register(RewardWallet)
class RewardWalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'credit', 'total_value']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    ordering = ['-points']
    
    def total_value(self, obj):
        """Show total value in a nice format"""
        return f"${obj.credit:.2f} + {obj.points} pts"
    total_value.short_description = 'Total Value'


@admin.register(RewardTransaction)
class RewardTransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'change_amount', 'reason', 'timestamp', 'formatted_amount']
    list_filter = ['reason', 'timestamp']
    search_fields = ['wallet__user__email', 'reason']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    def formatted_amount(self, obj):
        """Color code positive/negative amounts"""
        if obj.change_amount > 0:
            return format_html('<span style="color: green;">+{}</span>', obj.change_amount)
        else:
            return format_html('<span style="color: red;">{}</span>', obj.change_amount)
    formatted_amount.short_description = 'Amount'


@admin.register(RecyclingActivity)
class RecyclingActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'rvm', 'material', 'weight', 'points_earned', 'timestamp']
    list_filter = ['material', 'rvm', 'timestamp']
    search_fields = ['user__email', 'rvm__location', 'material__name']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp', 'points_earned']
    
    # make it read-only since points are auto-calculated
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing existing object
            return ['timestamp', 'points_earned', 'user', 'rvm', 'material', 'weight']
        return ['timestamp', 'points_earned']
