from django.contrib import admin
from .models import Counter, District, FileManager, Route, RouteStore, Store


@admin.register(Counter)
class CounterAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'get_is_active', 'created_at']
    list_filter = ['user__is_active', 'created_at']
    search_fields = ['employee_id', 'user__work_id', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'get_is_active']
    
    def get_is_active(self, obj):
        """Display the user's is_active status."""
        return obj.user.is_active if obj.user else False
    get_is_active.boolean = True
    get_is_active.short_description = 'Is Active'


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'priority', 'status', 'created_at']
    list_filter = ['priority', 'status', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'priority', 'address', 'status', 'latitude', 'longitude', 'created_at']
    list_filter = ['status', 'priority', 'district', 'created_at']
    search_fields = ['name', 'address', 'contact_person']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'user', 'date', 'status', 'approved_by', 'created_at']
    list_filter = ['status', 'district', 'date', 'created_at']
    search_fields = ['name', 'user__work_id', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'


@admin.register(RouteStore)
class RouteStoreAdmin(admin.ModelAdmin):
    list_display = ['route', 'store', 'order', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['route__name', 'store__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FileManager)
class FileManagerAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'user', 'route', 'file_type', 'purpose', 'bucket', 'is_active', 'file_size_mb', 'created_at']
    list_filter = ['file_type', 'purpose', 'bucket', 'is_active', 'created_at']
    search_fields = ['file_name', 'object_key', 'user__work_id', 'user__email', 'description', 'route__name']
    readonly_fields = ['file_size', 'file_size_mb', 'file_url', 'bucket', 'object_key', 'content_type', 'checksum', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    def file_size_mb(self, obj):
        """Display file size in MB."""
        return f"{obj.file_size_mb} MB" if obj.file_size_mb else "N/A"
    file_size_mb.short_description = 'File Size (MB)'
