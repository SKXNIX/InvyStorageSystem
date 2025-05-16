from django.contrib import admin
from django.db.models import F
# from django.contrib.auth.models import User
from django.contrib.admin.views.main import ChangeList
from django.urls import reverse
from django.utils.html import format_html

from apps.store.models import Place
from apps.custom_auth.models import CustomUser


class PlaceChildInline(admin.TabularInline):
    model = Place
    fk_name = 'parent'
    extra = 1
    fields = ('name', 'type', 'capacity', 'temperature', 'identifier')
    verbose_name = "Дочернее место"
    verbose_name_plural = "Дочерние места"


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'capacity', 'parent', 'full_path')
    list_filter = ('type', 'parent')
    search_fields = ('name', 'identifier')
    inlines = [PlaceChildInline]
    fieldsets = (
        (None, {'fields': ('name', 'type', 'parent', 'identifier')}),
        ('Характеристики', {'fields': ('capacity', 'temperature'),
                            'classes': ('collapse',)
                            }),
        )

    def full_path(self, obj):
        path = []
        current = obj
        while current:
            path.append(current.name)
            current = current.parent
        return ' → '.join(reversed(path))
    full_path.short_description = "Полный путь"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.role == 'admin' and not request.user.is_superuser:
            return qs.none()
        return qs

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.role == 'admin':
            return True
        return False

    def has_add_permission(self, request):
        return self.has_change_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self.has_delete_permission(request)

admin.site.register(Place, PlaceAdmin)
