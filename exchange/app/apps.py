from django.apps import AppConfig
from .models import Bank


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        print("ready...")
        from job import schedule, updates
        try:
            bank = models.Bank(currency="bitcoin")
            if not bank:
                AppConfig.makeBank("bitcoin")

            schedule.startSchedule()
            print("The scheduler has started")

        except Exception as e:
            print("The scheduler is not running, check console for details ")
            print(e, e.args)
        return

    def makeBank(currency):
        print(f"Bank is None, creating one for : {currency}")
        bank = models.Bank(currency=currency)
        return bank
