from datetime import timedelta
import math

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from usuarios.permissions import IsDefesaCivilOrAdmin
from .models import Medicao, PontoRisco
from .services.previsao import ForecastError, demo_readings, forecast


class ForecastThrottle(UserRateThrottle):
    scope = 'forecast'
    rate = '12/min'


class ReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicao
        fields = ['nivel', 'registrado_em']

    def validate_nivel(self, value):
        if not math.isfinite(value) or not 0 <= value <= 100:
            raise serializers.ValidationError('Informe um nível finito entre 0 e 100 metros.')
        return value

    def validate_registrado_em(self, value):
        if value > timezone.now():
            raise serializers.ValidationError('O horário não pode estar no futuro.')
        return value


class ForecastInput(serializers.Serializer):
    demonstracao = serializers.BooleanField(default=False)


class PointView(APIView):
    permission_classes = [IsDefesaCivilOrAdmin]
    throttle_classes = [ForecastThrottle]

    def point(self, pk):
        return get_object_or_404(PontoRisco, pk=pk)


class ReadingView(PointView):
    def post(self, request, pk):
        point = self.point(pk)
        serializer = ReadingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reading, created = Medicao.objects.get_or_create(ponto=point,
            registrado_em=serializer.validated_data['registrado_em'],
            defaults={'nivel': serializer.validated_data['nivel']})
        if not created and reading.nivel != serializer.validated_data['nivel']:
            return Response({'detail': 'Já existe outra leitura neste horário.'}, status=409)
        return Response(ReadingSerializer(reading).data, status=201 if created else 200)


class ForecastView(PointView):
    def post(self, request, pk):
        point = self.point(pk)
        serializer = ForecastInput(data=request.data)
        serializer.is_valid(raise_exception=True)
        demo = serializer.validated_data['demonstracao']
        if demo:
            readings = demo_readings(point)
        else:
            rows = list(point.medicoes.filter(registrado_em__gte=timezone.now()-timedelta(hours=6))
                        .order_by('-registrado_em')[:72])
            readings = [{'horario': r.registrado_em, 'nivel': r.nivel} for r in reversed(rows)]
        try:
            return Response(forecast(point, readings, demo))
        except ForecastError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
