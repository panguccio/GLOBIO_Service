from datetime import datetime
from storage.cache_manager import CacheManager
from loaders.argo_loader import fetch_profiles


start_date = datetime(2020, 7, 13).strftime("%Y-%m-%d")
end_date = datetime(2020, 8, 27).strftime("%Y-%m-%d")

region = [-5, 36, 30, 46, 0, 2000, start_date, end_date]
params = ['TEMP', 'PSAL', 'DOXY', 'CHLA', 'NITRATE', 'PRES']

cache = CacheManager()
profiles = fetch_profiles(mode='standard', params=params, region=region)
print("Argo data downloaded. Saving in cache...")
cache.save_data(profiles=profiles)
print("Argo data saved.")
