# admin.py

from django.contrib import admin
from .models import Book
from .forms import BookForm

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    form = BookForm
