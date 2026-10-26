from datetime import datetime
from storage.cache_manager import MemoryManager
from loaders.argo_loader import ArgopyLoader


start_date = datetime(2020, 7, 13).strftime("%Y-%m-%d")
end_date = datetime(2020, 8, 27).strftime("%Y-%m-%d")

region = [-5, 36, 30, 46, 0, 2000, start_date, end_date]
params = ['TEMP', 'PSAL', 'DOXY', 'CHLA', 'NITRATE', 'PRES']

memory = MemoryManager()
loader = ArgopyLoader()

index_df = loader.get_index_box(region[:4] + region[6:]) # index doesn't need pressure
# missing: logic to check if already downloaded

profiles = loader.fetch_profiles(mode='standard', params=params, region=region)
print("Argo data downloaded. Saving in memory...")
memory.save_data(profiles=profiles)
print("Argo data saved.")
