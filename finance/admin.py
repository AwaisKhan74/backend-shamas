from django.contrib import admin
from .models import Reward, UserReward, UserPoints, PointsTransaction, Withdrawal, FinanceTransaction


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_required', 'value', 'is_active', 'created_by', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ['user', 'reward', 'amount', 'points_earned', 'activity_type', 'status', 'earned_at', 'awarded_by']
    list_filter = ['status', 'activity_type', 'earned_at']
    search_fields = ['user__work_id', 'reward__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'earned_at'


@admin.register(UserPoints)
class UserPointsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'available_points', 'lifetime_points', 'updated_at']
    list_filter = ['updated_at']
    search_fields = ['user__work_id', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-total_points']


@admin.register(PointsTransaction)
class PointsTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'transaction_type', 'activity_type', 'points', 'store', 'created_at']
    list_filter = ['transaction_type', 'activity_type', 'created_at']
    search_fields = ['user__work_id', 'description', 'store__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'request_date', 'processed_by', 'transaction_id']
    list_filter = ['status', 'request_date']
    search_fields = ['user__work_id', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'request_date'


@admin.register(FinanceTransaction)
class FinanceTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_type', 'amount', 'related_user', 'date', 'recorded_by']
    list_filter = ['transaction_type', 'date']
    search_fields = ['related_user__work_id', 'description']
    readonly_fields = ['created_at']
    date_hierarchy = 'date'
