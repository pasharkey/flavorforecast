from dgm import api
import datetime

flavor_forecast = api.DGMApi()


dt = datetime.datetime.now()
print(flavor_forecast.search(dt))
#print(flavor_forecast.search('2017-08-27'))

print(flavor_forecast.get_status())

print(flavor_forecast.operating_hours(datetime.datetime.now()))

#print(flavor_forecast.closed_now())

#print(flavor_forecast.time_until_open())
#print(flavor_forecast.time_until_closed())

