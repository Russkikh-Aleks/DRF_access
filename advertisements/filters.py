from django_filters import rest_framework as filters
from django_filters import DateFromToRangeFilter

from advertisements.models import Advertisement
from django_filters.rest_framework import DjangoFilterBackend


class AdvertisementFilter(filters.FilterSet):
    """Фильтры для объявлений."""

    # TODO: задайте требуемые фильтры
    created_at = DateFromToRangeFilter()
    creator = DjangoFilterBackend
    status = DjangoFilterBackend

    class Meta:
        model = Advertisement
        fields = ['created_at', 'creator', 'status']

   
