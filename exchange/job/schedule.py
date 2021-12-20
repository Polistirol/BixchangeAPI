from apscheduler.schedulers.background import BackgroundScheduler
from job.updates import fetchDataFromApi, getBankStats


def startSchedule():

    fetchDataFromApi()
    getBankStats()

    secondsForSchedule = 60

    scheduler = BackgroundScheduler(timezone="Europe/Berlin",)
    scheduler.add_job(fetchDataFromApi, 'interval',
                      seconds=secondsForSchedule,)
    scheduler.add_job(getBankStats, 'interval', seconds=secondsForSchedule)
    scheduler.start()
