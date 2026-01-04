# backend/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from easy_thumbnails.files import get_thumbnailer

from backend.models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, \
    Contact, ConfirmEmailToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Панель управления пользователями с поддержкой аватаров
    """
    model = User
    list_display = ('email', 'first_name', 'last_name', 'type', 'is_active', 'avatar_preview', 'social_provider')
    list_filter = ('type', 'is_active', 'is_staff', 'social_provider')
    search_fields = ('email', 'first_name', 'last_name', 'company')
    readonly_fields = ('avatar_preview', 'date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password', 'type')}),
        ('Персональная информация', {
            'fields': ('first_name', 'last_name', 'company', 'position', 'avatar', 'avatar_preview')
        }),
        ('Социальная авторизация', {
            'fields': ('social_id', 'social_provider'),
            'classes': ('collapse',)
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />',
                obj.get_avatar_thumbnail((50, 50))
            )
        return "Нет аватара"

    avatar_preview.short_description = 'Аватар'


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'state', 'url')
    list_filter = ('state',)
    search_fields = ('name', 'user__email')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_shops_count')
    filter_horizontal = ('shops',)

    def get_shops_count(self, obj):
        return obj.shops.count()

    get_shops_count.short_description = 'Количество магазинов'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'shop', 'price', 'quantity', 'external_id')
    list_filter = ('shop',)
    search_fields = ('product__name', 'model', 'external_id')


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    pass


@admin.register(ProductParameter)
class ProductParameterAdmin(admin.ModelAdmin):
    list_display = ('product_info', 'parameter', 'value')
    list_filter = ('parameter',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'state', 'dt', 'contact')
    list_filter = ('state', 'dt')
    search_fields = ('user__email', 'contact__phone')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_info', 'quantity')
    list_filter = ('order__state',)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'street', 'house', 'phone')
    search_fields = ('user__email', 'city', 'phone')


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)
    search_fields = ('user__email', 'key')