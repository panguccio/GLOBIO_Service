from datetime import datetime

from processing.input_formatter import WmoDataset
from storage.cache_manager import MemoryManager
from loaders.argo_loader import ArgopyLoader

def get_profiles(start_date: str = datetime(2020, 7, 13).strftime("%Y-%m-%d"),
                 end_date: datetime = datetime(2020, 8, 27).strftime("%Y-%m-%d")):

    region = [-5, 36, 30, 46, 0, 2000, start_date, end_date]
    params = ['TEMP', 'PSAL', 'DOXY', 'CHLA', 'NITRATE', 'PRES']
    params_simple = ['PSAL', 'DOXY']

    memory = MemoryManager()
    loader = ArgopyLoader()

    index_df = loader.get_index_box(region[:4] + region[6:]) # index box doesn't need pressure
    # missing: logic to check if already downloaded

    profiles = loader.fetch_profiles(mode='standard', params=params, region=region)
    print("Argo data downloaded. Saving in memory...")
    memory.save_netcdf(profiles=profiles)
    print("Argo data saved.")


if __name__ == "__main__":
    mm = MemoryManager()
    existing = mm.get_existing_profiles()
    dataset = WmoDataset(existing)
    print(dataset[0])

