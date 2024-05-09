from django.contrib.auth.models import AnonymousUser
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from advertisements.filters import AdvertisementFilter
from advertisements.models import Advertisement, Favorits
from advertisements.permissions import IsOwnerAdminOrReadOnly
from advertisements.serializers import AdvertisementSerializer


class AdvertisementViewSet(ModelViewSet):
    """ViewSet для объявлений."""
    # TODO: настройте ViewSet, укажите атрибуты для кверисета,
    #   сериализаторов и фильтров

    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filterset_class = AdvertisementFilter

    def list(self, request):
        queryset = self.get_queryset()
        queryset = AdvertisementFilter(
            data=request.GET, queryset=queryset, request=request).qs
        serializer = AdvertisementSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        user = self.request.user

        if isinstance(user, AnonymousUser):
            return Advertisement.objects.filter(status__in=["OPEN", "CLOSED"])
        if user.is_superuser:
            return Advertisement.objects.all()
        return Advertisement.objects.filter(
            status__in=["OPEN", "CLOSED"]) | Advertisement.objects.filter(creator=user)

    def get_permissions(self):
        """Получение прав для действий."""
        if self.action in ["create", "destroy", "update", "partial_update"]:
            return [IsAuthenticated(), IsOwnerAdminOrReadOnly()]
        return []

    @action(detail=True, methods=['POST'])
    def mark_as_favorite(self, request, pk=None):
        """Добавление объявлений в список избранного"""
        user = request.user
        if isinstance(user, AnonymousUser):
            return Response({"message": "Анонимные пользователи не могут добавлять объявления в избранное"}, status=404)

        try:
            advertisement = self.get_object()
        except Advertisement.DoesNotExist:
            return Response({"error": "Объявление не найдено"}, status=404)

        if advertisement.creator == user:
            return Response({"message": "Автор объявления не может добавлять его в избранное"}, status=404)

        object = Favorits.objects.filter(
            user=user).filter(advertisement=advertisement)
        if object:
            return Response({"message": f"Объявление с id {advertisement.id} уже в списке избранного {user}."}, status=200)

        Favorits(advertisement=advertisement, user=request.user).save()
        return Response({"message": f"Объявление с id {advertisement.id} добавлено в список избранного {user}."}, status=200)

    @action(detail=False, methods=['GET'])
    def favorite_advertisements(self, request):
        """Просмотр объявлений из списка избранного пользователя"""
        user = request.user

        if isinstance(user, AnonymousUser):
            return Response({"message": "Для просмотра избранных объявлений пройдите аутентификацию"}, status=404)

        favorite_advertisement = user.advertisements.all()
        serializer = self.get_serializer(favorite_advertisement, many=True)
        return Response(serializer.data)
