from django.contrib import admin
from .models import InsightPanel, Dataset, DownloadableFile, DownloadHistory, FAQ


@admin.register(InsightPanel)
class InsightPanelAdmin(admin.ModelAdmin):
    list_display = ['title', 'data_source', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description', 'data_source']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    search_fields = ['name', 'description', 'owner__work_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DownloadableFile)
class DownloadableFileAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_type', 'size', 'uploaded_by', 'created_at']
    list_filter = ['file_type', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'file', 'download_timestamp']
    list_filter = ['download_timestamp']
    search_fields = ['user__work_id', 'file__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'download_timestamp'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    readonly_fields = ['created_at', 'updated_at']
