from django.contrib import admin
from .models import Product,ProImage,ProColors,ProSizes,Category,MatCategory,Collection,CollectionItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('Title', 'Description', 'Active', 'Slug')
    search_fields = ('Title', 'Description')
    prepopulated_fields = {'Slug': ('Title',)}

@admin.register(MatCategory)
class MatCategoryAdmin(admin.ModelAdmin):
    list_display = ('Title', 'Active', 'Slug')
    search_fields = ('Title',)
    prepopulated_fields = {'Slug': ('Title',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('ProductName', 'Supplier', 'UnitPrice', 'Stock', 'OutOfStock', 'DiscountAvailable', 'Rating', 'Publish_Date')
    search_fields = ('ProductName', 'Supplier__user__email', 'Supplier__user__first_name', 'Supplier__user__last_name')
    list_filter = ('OutOfStock', 'DiscountAvailable', 'Rating', 'Publish_Date')
    ordering = ('-Publish_Date',)

@admin.register(ProImage)
class ProImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    search_fields = ('product__ProductName',)

@admin.register(ProColors)
class ProColorsAdmin(admin.ModelAdmin):
    list_display = ('product', 'Color')
    search_fields = ('product__ProductName', 'Color')

@admin.register(ProSizes)
class ProSizesAdmin(admin.ModelAdmin):
    list_display = ('product', 'Size')
    search_fields = ('product__ProductName', 'Size')

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'supplier')
    search_fields = ('name', 'supplier__user__email', 'supplier__user__first_name', 'supplier__user__last_name')

@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    list_display = ('collection', 'product')
    search_fields = ('collection__name', 'product__ProductName')
