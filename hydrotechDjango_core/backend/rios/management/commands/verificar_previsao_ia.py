"""Read-only live smoke test; never logs credentials or provider error bodies."""
from types import SimpleNamespace
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError
from rios.services.previsao import demo_readings, forecast, ForecastError


class Command(BaseCommand):
    help = 'Valida a integração real com Gemini usando uma série simulada, sem gravar dados.'

    def handle(self, *args, **options):
        point = SimpleNamespace(pk='smoke-test', limite_emergencia=3.5)
        cache.clear()
        try:
            result = forecast(point, demo_readings(point), demo=True)
        except ForecastError as exc:
            raise CommandError(str(exc)) from None
        if not result.get('ia'):
            raise CommandError('Gemini não configurado. Defina GEMINI_API_KEY no ambiente seguro do backend.')
        self.stdout.write(self.style.SUCCESS('Gemini respondeu com previsão válida para dados simulados.'))
        self.stdout.write(f"Modelo: {result['ia']['modelo']}; estimativa: {result['ia']['horas_estimadas']} h")
