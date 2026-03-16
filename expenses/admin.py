# expenses/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import ExpenseCategory, Expense

@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    """Admin interface for ExpenseCategory model"""
    
    list_display = [
        'name',
        'description_truncated',
        'expense_count',
        'total_expenses',
        'status_badge',
        'created'
    ]
    
    list_filter = [
        'is_active',
        'created',
        'updated'
    ]
    
    search_fields = [
        'name',
        'description'
    ]
    
    readonly_fields = [
        'created',
        'updated',
        'expense_stats'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Status', {
            'fields': ('is_active', 'is_deleted')
        }),
        ('Statistics', {
            'fields': ('expense_stats',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )
    
    def description_truncated(self, obj):
        """Display truncated description"""
        if obj.description:
            truncated = obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
            return format_html(
                '<span title="{}">{}</span>',
                obj.description,
                truncated
            )
        return format_html('<em style="color: #6c757d;">No description</em>')
    description_truncated.short_description = 'Description'
    
    def expense_count(self, obj):
        """Display number of expenses in this category"""
        count = obj.expenses.filter(is_deleted=False).count()
        return format_html(
            '<span style="background-color: #2196F3; color: white; padding: 3px 8px; border-radius: 3px;"><strong>{}</strong></span>',
            count
        )
    expense_count.short_description = 'Expenses'
    
    def total_expenses(self, obj):
        """Display total amount of expenses in this category"""
        total = obj.expenses.filter(is_deleted=False).aggregate(total=Sum('amount'))['total'] or 0
        
        return format_html(
            '<span style="color: #28a745;"><strong>{:.2f}</strong></span>',
            total
        )
    total_expenses.short_description = 'Total Amount'
    
    def status_badge(self, obj):
        """Display category status"""
        if obj.is_active and not obj.is_deleted:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">✓ Active</span>'
            )
        
        if obj.is_deleted:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">✗ Deleted</span>'
            )
        
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px;">⊘ Inactive</span>'
        )
    status_badge.short_description = 'Status'
    
    def expense_stats(self, obj):
        """Display expense statistics"""
        total_count = obj.expenses.filter(is_deleted=False).count()
        total_amount = obj.expenses.filter(is_deleted=False).aggregate(total=Sum('amount'))['total'] or 0
        confirmed_amount = obj.expenses.filter(is_deleted=False, status='Confirmed').aggregate(total=Sum('amount'))['total'] or 0
        
        return format_html(
            '<div style="padding: 10px; background-color: #f5f5f5; border-radius: 4px;">'
            '<strong>Total Expenses:</strong> {}<br>'
            '<strong>Total Amount:</strong> {:.2f}<br>'
            '<strong>Confirmed Amount:</strong> {:.2f}'
            '</div>',
            total_count,
            total_amount,
            confirmed_amount
        )
    expense_stats.short_description = 'Expense Statistics'
    
    def created(self, obj):
        """Display creation timestamp"""
        return obj.created.strftime('%Y-%m-%d %H:%M:%S')
    created.short_description = 'Created'
    created.admin_order_field = 'created'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.order_by('-created')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Admin interface for Expense model"""
    
    list_display = [
        'description_or_category',
        'amount_display',
        'category_display',
        'expense_date_display',
        'status_badge',
        'recorded_by_display',
        'created'
    ]
    
    list_filter = [
        'status',
        'category',
        'expense_date',
        'is_active',
        'created',
        ('recorded_by', admin.RelatedOnlyFieldListFilter)
    ]
    
    search_fields = [
        'description',
        'category__name',
        'recorded_by__first_name',
        'recorded_by__last_name',
        'recorded_by__email',
        'amount'
    ]
    
    readonly_fields = [
        'created',
        'updated',
        'content_object_display',
        'currency_info',
        'proof_preview',
        'workflow_info',
    ]
    
    fieldsets = (
        ('Expense Information', {
            'fields': ('category', 'description', 'amount', 'expense_date')
        }),
        ('Currency & Exchange Rate', {
            'fields': ('currency', 'currency_info', 'rate_at_expense_date')
        }),
        ('Recording Details', {
            'fields': ('recorded_by', 'proof', 'proof_preview')
        }),
        ('Workflow & Approval', {
            'fields': (
                'status',
                'workflow_info'
            )
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_uid', 'content_object_display'),
            'classes': ('collapse',)
        }),
        ('Status Management', {
            'fields': ('is_active', 'is_deleted'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created', 'updated'),
            'classes': ('collapse',)
        })
    )
    
    def description_or_category(self, obj):
        """Display description or category"""
        if obj.description:
            return obj.description
        return format_html(
            '<span style="color: #666;">{}</span>',
            obj.category.name if obj.category else 'N/A'
        )
    description_or_category.short_description = 'Description'
    
    def amount_display(self, obj):
        """Display amount with currency"""
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{:.2f} {}</span>',
            obj.amount,
            obj.currency.code if obj.currency else 'N/A'
        )
    amount_display.short_description = 'Amount'
    
    def category_display(self, obj):
        """Display category with link"""
        if obj.category:
            category_url = reverse('admin:expenses_expensecategory_change', args=[obj.category.uid])
            return format_html(
                '<a href="{}">{}</a>',
                category_url,
                obj.category.name
            )
        return format_html('<em style="color: #6c757d;">Uncategorized</em>')
    category_display.short_description = 'Category'
    
    def expense_date_display(self, obj):
        """Display expense date"""
        return obj.expense_date.strftime('%Y-%m-%d')
    expense_date_display.short_description = 'Expense Date'
    expense_date_display.admin_order_field = 'expense_date'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        status_colors = {
            'Draft': '#757575',
            'Submitted': '#2196F3',
            'Reverted': '#FF9800',
            'Rejected': '#F44336',
            'Cancelled': '#9E9E9E',
            'Confirmed': '#4CAF50',
        }
        color = status_colors.get(obj.status, '#757575')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    
    def recorded_by_display(self, obj):
        """Display user who recorded expense"""
        if obj.recorded_by:
            user_url = reverse('admin:auth_user_change', args=[obj.recorded_by.id])
            return format_html(
                '<a href="{}">{}</a>',
                user_url,
                obj.recorded_by.get_full_name() or obj.recorded_by.username
            )
        return format_html('<em style="color: #6c757d;">Unknown</em>')
    recorded_by_display.short_description = 'Recorded By'
    
    def currency_info(self, obj):
        """Display currency information"""
        if obj.currency:
            return format_html(
                '<div style="padding: 10px; background-color: #e3f2fd; border-radius: 4px;">'
                '<strong>Code:</strong> {}<br>'
                '<strong>Name:</strong> {}<br>'
                '<strong>Symbol:</strong> {}'
                '</div>',
                obj.currency.code,
                obj.currency.name if hasattr(obj.currency, 'name') else 'N/A',
                obj.currency.symbol if hasattr(obj.currency, 'symbol') else 'N/A'
            )
        return format_html('<em style="color: #6c757d;">No currency assigned</em>')
    currency_info.short_description = 'Currency Details'
    
    def proof_preview(self, obj):
        """Display proof file preview"""
        if obj.proof:
            return format_html(
                '<div style="padding: 10px; background-color: #f5f5f5; border-radius: 4px;">'
                '<strong>File:</strong> <a href="{}" target="_blank">{}</a><br>'
                '<strong>Size:</strong> {:.2f} KB'
                '</div>',
                obj.proof.url,
                obj.proof.name.split('/')[-1],
                obj.proof.size / 1024
            )
        return format_html(
            '<div style="padding: 10px; background-color: #fff3e0; border-radius: 4px;">'
            '<em>No proof uploaded</em>'
            '</div>'
        )
    proof_preview.short_description = 'Proof of Expense'
    
    def content_object_display(self, obj):
        """Display related content object"""
        if obj.content_object:
            content_str = str(obj.content_object)
            return format_html(
                '<div style="padding: 10px; background-color: #e8f5e9; border-radius: 4px;">'
                '<strong>Type:</strong> {}<br>'
                '<strong>Object:</strong> {}'
                '</div>',
                obj.content_type.name if obj.content_type else 'Unknown',
                content_str
            )
        return format_html(
            '<div style="padding: 10px; background-color: #f5f5f5; border-radius: 4px;">'
            '<em>No related object</em>'
            '</div>'
        )
    content_object_display.short_description = 'Related Object'
    
    def workflow_info(self, obj):
        """Display workflow information"""
        workflow_data = obj.get_workflow_display_format()
        
        items = []
        for key, value in workflow_data.items():
            items.append(f"<strong>{key}:</strong> {value}")
        
        return format_html(
            '<div style="padding: 10px; background-color: #f5f5f5; border-radius: 4px;">{}</div>',
            '<br>'.join(items)
        )
    workflow_info.short_description = 'Workflow Information'
    
    
    def created(self, obj):
        """Display creation timestamp"""
        return obj.created.strftime('%Y-%m-%d %H:%M:%S')
    created.short_description = 'Created'
    created.admin_order_field = 'created'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('category', 'currency', 'recorded_by', 'content_type', 'rate_at_expense_date').order_by('-created')
    
    def get_readonly_fields(self, request, obj=None):
        """Make fields read-only based on expense status"""
        readonly = list(self.readonly_fields)
        
        if obj and not obj.is_editable():
            readonly.extend(['category', 'description', 'amount', 'expense_date', 'currency', 'recorded_by', 'proof'])
        
        return readonly

