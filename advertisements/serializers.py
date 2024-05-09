from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework import serializers

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        # TODO: добавьте требуемую валидацию
        user = self.context["request"].user

        if self.context["request"].method == 'POST' and data["status"] == "OPEN":
            count = len(Advertisement.objects.filter(
                creator=user).filter(status='OPEN'))
            if count >= 10:
                raise ValidationError(
                    'У вас должно быть не более 10 открытых объявлений')

        status = data.get('status')
        if self.context["request"].method == 'PATCH' and status and status == "OPEN":
            pk = int(self.context["request"].parser_context["kwargs"]["pk"])
            adv_status = Advertisement.objects.filter(pk=pk)[0].status
            adv_creator = Advertisement.objects.filter(pk=pk)[0].creator
            count = len(Advertisement.objects.filter(
                creator=adv_creator).filter(status='OPEN'))

            if adv_status in ("CLOSED", "DRAFT") and count >= 10:
                raise ValidationError(
                    f'У пользователя {adv_creator} должно быть не более 10 открытых объявлений')

        return data
