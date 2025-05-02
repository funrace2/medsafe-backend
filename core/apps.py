# core/apps.py

from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = "core"            # 앱의 실제 이름
    verbose_name = "Core"

    def ready(self):
        # 앱이 로드될 때 signals.py 안의 핸들러를 등록
        import core.signals  # noqa
