"""
    This is currently a place for helper functions using the data from the
    Wunderground API
    http://api.wunderground.com/weather/api/d/docs
"""

def sunny(forecast_icon):
    sunny_values = [
        'clear',
        'partlysunny',
        'mostlysunny',
        'sunny',
    ]
    return forecast_icon in sunny_values

def precipitating(forecast_icon):
    precip_values = [
        'flurries',
        'sleet',
        'rain',
        'snow',
        'tstorms',
    ]
    return forecast_icon in precip_values