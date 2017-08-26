from dgm import api
import datetime

flavor_forecast = api.DGMApi()


# date 05-29-2017 has a `-` in the result
date_dash = datetime.datetime.strptime('2017-05-29', '%Y-%m-%d')
print "date dash:", flavor_forecast.search(date_dash)

# date 05-02-2017 has `Closed Tuesdays` in the result
date_closed_long = datetime.datetime.strptime('2017-05-02', '%Y-%m-%d')
print "date cloased long:", flavor_forecast.search(date_closed_long)

# date 05-30-2017 has `Closed` in the result
date_closed_short = datetime.datetime.strptime('2017-05-30', '%Y-%m-%d')
print "date closed short:", flavor_forecast.search(date_closed_short)

# date 03-27-2017 has `(` in the result
date_paren = datetime.datetime.strptime('2017-03-27', '%Y-%m-%d')
print "date paren:", flavor_forecast.search(date_paren)

# date 03-25-2017 has `Banana Pudding` twice in the result
date_multi = datetime.datetime.strptime('2017-03-25', '%Y-%m-%d')
print "date paren:", flavor_forecast.search(date_multi)

# get the current status
print(flavor_forecast.get_status())

# date 03-25-2017 has `Banana Pudding` twice in the result
date_now = datetime.datetime.now()
print "date NOW:", flavor_forecast.search(date_now)

#print(flavor_forecast.operating_hours(datetime.datetime.now()))

#print(flavor_forecast.closed_now())

#print(flavor_forecast.time_until_open())
#print(flavor_forecast.time_until_closed())

