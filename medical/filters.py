from django_filters.rest_framework import FilterSet
from .models import Item

class ItemFilter(FilterSet):
  class Meta:
    model = Item
    fields = {
      'collection_id': ['exact'],
      'unit_price': ['gt', 'lt']
    }