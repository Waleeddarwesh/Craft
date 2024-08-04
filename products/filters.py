import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='iexact')
    keyword= django_filters.filters.CharFilter(field_name="ProductName",lookup_expr="icontains")
    min_price =django_filters.filters.NumberFilter(field_name="UnitPrice", lookup_expr='gte')
    max_price = django_filters.filters.NumberFilter(field_name="UnitPrice", lookup_expr='lte')    
    class Meta:
        model = Product
        fields =('Category','Supplier','keyword','min_price','max_price')

