from constance import config
import datetime


def days_subscription(request):    
    if request.user.is_authenticated():
        if request.user.profile.buy_date is not None:
            days = (datetime.date.today() - request.user.profile.buy_date).days
            days = config.V6_SUBSCRIPTION_DAYS - days            
            return {
                'days': days,
                'free': config.V7_WORLD_FREE_ACCESS,
                }
    return {
        'days': 0,
        'free': config.V7_WORLD_FREE_ACCESS,
        }
