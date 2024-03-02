from django.http import JsonResponse
from django.core.management import call_command





def run_daily_stock_data(request):
    # Call the management command to execute the daily_stock_data script
    call_command('daily_stock_data')
    return JsonResponse({'message': 'Daily stock data updated successfully'})



def run_realtime_data_collector(request):
    # Call the management command to execute the realtime_data_collector script
    call_command('realtime_data_collector')
    return JsonResponse({'message': 'Realtime data collection completed successfully'})


def run_historical_data_fetcher(request):
    # Call the management command to execute the historical_data script
    call_command('historical_data_storage')
    return JsonResponse({'message': 'Historical data fetched successfully'})




