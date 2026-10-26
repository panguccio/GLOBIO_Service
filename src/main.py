from datetime import datetime
from storage.cache_manager import CacheManager
from loaders.argo_loader import ArgopyLoader


start_date = datetime(2020, 7, 13).strftime("%Y-%m-%d")
end_date = datetime(2020, 8, 27).strftime("%Y-%m-%d")

region = [-5, 36, 30, 46, 0, 2000, start_date, end_date]
box = [-5, 36, 30, 46, start_date, end_date]
params = ['TEMP', 'PSAL', 'DOXY', 'CHLA', 'NITRATE', 'PRES']



cache = CacheManager()
loader = ArgopyLoader()

idx = loader.get_index(box).to_dataframe()
box_wmos = [path.split("/")[-1] for path in idx["file"]]
wmos, cycles = cache.check_cache(box_wmos)

idx = loader.idx_subset(wmos, cycles)

# logic to check if already downloaded

profiles = loader.fetch_profiles(mode='standard', params=params, region=region)
print("Argo data downloaded. Saving in cache...")
cache.save_data(profiles=profiles)
print("Argo data saved.")
