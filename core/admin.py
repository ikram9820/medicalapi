from medical.models import Item
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from medical.admin import ItemAdmin, ItemImageInline
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email','courtesy', 'first_name', 'last_name'),
        }),
    )




class CustomItemAdmin(ItemAdmin):
    inlines = [ItemImageInline]


admin.site.unregister(Item)
admin.site.register(Item, CustomItemAdmin)
