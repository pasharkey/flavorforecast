from dgm import api

flavor_forecast = api.DGMApi()

print(flavor_forecast.search('2017-08-22'))

#print(flavor_forecast.open_now())
#print(flavor_forecast.closed_now())

#print(flavor_forecast.time_until_open())
#print(flavor_forecast.time_until_closed())
