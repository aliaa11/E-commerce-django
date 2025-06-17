from django.contrib import admin

# Register your models here.
from .models import CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active']
    search_fields = ['username', 'email']
    list_filter = ['is_staff', 'is_active']
    readonly_fields = ['date_joined', 'last_login']
    
    def date_joined(self, obj):
        return obj.date_joined.strftime('%Y-%m-%d %H:%M:%S')
    
    date_joined.short_description = 'Date Joined'
    
    def last_login(self, obj):
        return obj.last_login.strftime('%Y-%m-%d %H:%M:%S') if obj.last_login else 'Never'
    
    last_login.short_description = 'Last Login'
    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser or (obj and obj == request.user)
    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)
    def delete_model(self, request, obj):
        if obj.is_superuser:
            self.message_user(request, "Cannot delete superuser accounts.", level='error')
            return
        super().delete_model(request, obj)
        self.message_user(request, "User deleted successfully.", level='success')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'last_login']
    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return (
                (None, {
                    'fields': ('username', 'email', 'first_name', 'last_name', 'password')
                }),
                ('Permissions', {
                    'fields': ('is_staff', 'is_active', 'is_superuser')
                }),
                ('Important dates', {
                    'fields': ('date_joined', 'last_login')
                }),
            )
        return (
            (None, {
                'fields': ('username', 'email', 'first_name', 'last_name')
            }),
            ('Important dates', {
                'fields': ('date_joined', 'last_login')
            }),
        )
