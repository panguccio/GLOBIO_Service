from datetime import datetime
from storage.cache_manager import CacheManager
from loaders.argo_loader import fetch_data
from processing.processing import convert_unit

start_date = datetime(2020, 7, 13).strftime("%Y-%m-%d")
end_date = datetime(2020, 7, 27).strftime("%Y-%m-%d")

region = [-5, 36, 30, 46, 0, 2000, start_date, end_date]
params = ['TEMP', 'PSAL', 'DOXY', 'CHLA', 'NITRATE', 'PRES']

cache = CacheManager()

if cache.dir_exists(start_date=start_date, end_date=end_date):
    print("Argo data found in cache. Loading...")
    data = []
    pass # aggiungere logica di recupero dato
else:
    print("Argo data not found in cache. Downloading...")
    data = fetch_data(mode='standard', params=params, region=region)
    print("Argo data downloaded. Saving in cache...")
    cache_path = cache.create_dir(start_date=start_date, end_date=end_date)
    cache.save_data(data=data, path=cache_path)
    print("Argo data saved.")

data = convert_unit(data)

print(data['CHLA'])