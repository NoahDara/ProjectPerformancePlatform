from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q
from helpers.models import BaseModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
User = get_user_model()
from django.urls import reverse


# Create your models here.
class ExpenseCategory(BaseModel):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(blank=True, null=True, max_length=255)


    def __str__(self):
        return f"{self.name} - ({self.code})"
    
class Expense(BaseModel):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Reverted', 'Reverted'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
        ('Confirmed', 'Confirmed'),
    ]
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, null=True, blank=True, related_name='expenses',)
    category = models.ForeignKey('ExpenseCategory', on_delete=models.SET_NULL, null=True, related_name='expenses',
                                 limit_choices_to=Q(is_active=True, is_deleted=False))
    
    description = models.CharField(blank=True, null=True, max_length=255)
    amount = models.FloatField()
    expense_date = models.DateField(default=timezone.now)
    status = models.CharField(choices=STATUS_CHOICES, default='Draft', max_length=20)
    proof = models.FileField(upload_to='expenses_proof/', blank=True, null=True, help_text="Upload proof of expense (e.g., receipt)")

    def __str__(self):
        content_str = f"{self.content_object} - " if self.content_object else ""
        return f"{content_str}{self.category.name} - {self.amount}"
    
        
    def is_editable(self):
        return self.status in ["Draft", "Rejected", "Reverted"]
    