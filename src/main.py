from datetime import datetime
from processing.input_formatter import WmoDataset
from storage.cache_manager import MemoryManager
from loaders.argo_loader import ArgopyLoader
from graphics.plotter import plot_comparison
from processing.conversions import convert_mmol
from processing.netcdf_formatter import convert_argo_to_standard


def get_profiles(start_date: str = datetime(2020, 7, 13).strftime("%Y-%m-%d"),
                 end_date: datetime = datetime(2020, 7, 16).strftime("%Y-%m-%d"),
                 cache_dir: str = "data"):

    region = [-5, 36, 30, 46, 0, 2000, start_date, end_date]
    params = ['TEMP', 'PSAL', 'DOXY', 'CHLA', 'NITRATE', 'PRES']
    params_simple = ['DOXY']

    memory = MemoryManager(cache_dir)
    loader = ArgopyLoader()

    index_df = loader.get_index_box(region[:4] + region[6:]) # index box doesn't need pressure
    # missing: logic to check if already downloaded

    profiles = loader.fetch_profiles(mode='standard', params=params_simple, region=region)
    print("Argo data downloaded. Saving in memory...")
    profiles = convert_mmol(profiles)
    profiles = convert_argo_to_standard(profiles)
    # profiles = convert_argo_to_standard(profiles)
    memory.save_profiles(profiles=profiles, replace=True)
    print("Argo data saved.")

def to_dataset():
    mm = MemoryManager()
    existing = mm.get_profiles_paths()
    example_paths = ["data/6901774/SD6901774_113.nc", "example_data/6901774/SR6901774_113.nc"]
    dataset = WmoDataset(example_paths, ['DOXY', 'PSAL', 'TEMP', 'PRES', 'PRES_DOXY', 'PRES_TEMP', 'PRES_PSAL'])
    return dataset


if __name__ == "__main__":
    pass

