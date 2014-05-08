import os
import vcr

from datetime import datetime
from requests_forecast import Forecast


def main():
    record_mode = 'none'  # 'none', 'new_episodes', 'all', 'once'
    #serializer = 'yaml'
    #fixtures_path = 'fixtures/{}.{}'.format(record_mode, serializer)
    #with vcr.use_cassette(fixtures_path, serializer=serializer, record_mode=record_mode):

    with vcr.use_cassette('fixtures/current.yaml', record_mode=record_mode):
        time = datetime(2013, 3, 28, 19, 8, 25)
        #time = datetime.now()
        forecast = Forecast(os.environ.get('FORECAST_IO_API'),
                            latitude=38.9717,
                            longitude=-95.235,
                            time=time)  # (year=2013, month=12, day=29, hour=12))
        print '+' * 20

        currently = forecast.get_currently()
        print 'current.temperature: {}'.format(currently.temperature)
        print 'current.cloudCover: {}'.format(currently.cloudCover)
        print 'current.humidity: {}'.format(currently.humidity)
        print 'current.icon: {}'.format(currently.icon)
        #print 'current.precipIntensity: {}'.format(currently.get('precipIntensity'))
        print 'current.precipIntensity: {}'.format(currently.precipIntensity)
        print 'current.pressure: {}'.format(currently.pressure)
        print 'current.summary: {}'.format(currently.summary)
        print 'current.time: {}'.format(currently.time)
        print 'current.visibility: {}'.format(currently.visibility)
        print 'current.windBearing: {}'.format(currently.windBearing)
        print 'current.windSpeed: {}'.format(currently.windSpeed)
        #print 'current: {}'.format(currently)
        print '-' * 20

        daily = forecast.get_daily()
        print 'daily: {}'.format(len(daily))
        #print 'daily: {}'.format(daily.data)
        for day in daily.data:
            print '- {} | {} | {} | {}'.format(day.sunriseTime, day.sunsetTime, day.temperatureMin, day.temperatureMax)

        #import ipdb
        #ipdb.set_trace()

        import pytz
        print '++', str(currently.time.astimezone(pytz.utc))
        print '--', str(currently.time)

        print '-' * 20
        print 'daily: {}'.format(daily['data'][0]['temperatureMin'])
        print 'daily: {}'.format(daily['data'][0]['temperatureMax'])
        print 'daily: {}'.format(daily)

        hourly = forecast.get_hourly()
        print 'hourly: {}'.format(len(hourly['data']))
        #print 'minutely: {}'.format(len(forecast.minutely['data']))

        alerts = forecast.get_alerts()
        print alerts


if __name__ == '__main__':
    main()
