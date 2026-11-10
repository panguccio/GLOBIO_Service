from datetime import datetime
from processing.input_formatter import WmoDataset
from storage.cache_manager import MemoryManager
from loaders.argo_loader import ArgopyLoader
from processing.conversions import convert_mmol
from processing.netcdf_formatter import convert_argo_to_standard
from graphics.plotter import plot_similar_comparison



if __name__ == "__main__":
    loader = ArgopyLoader()

    params = ['TEMP', 'PSAL', 'DOXY', 'CHLA', 'NITRATE', 'PRES']

    # load single profiles
    standard_profile = loader.fetch_profile(wmo=6901774, cycle=112, params=params)
    expert_profile = loader.fetch_profile(wmo=6901774, cycle=112, params=params, mode="expert")

    # load multiple profiles from a region and a time interval
    start_date = datetime(2020, 7, 1).strftime("%Y-%m-%d")
    end_date = datetime(2020, 8, 1).strftime("%Y-%m-%d")
    region = [-5, 36, 30, 46, 0, 2000, start_date, end_date]

    profiles = loader.fetch_profiles(region=region)

    print("Argo data downloaded. Saving in memory...")

    # preprocessing conversions
    profiles = convert_mmol(profiles)
    profiles = convert_argo_to_standard(profiles)

    # saving the profiles in memory
    memory = MemoryManager("data/test")
    memory.save_profiles(profiles=profiles, replace=True)

    # plotting a comparison of profiles
    name_profiles_ses = {
        "STANDARD": standard_profile,
        "EXPERT": expert_profile,
        "SUPERFLOAT": MemoryManager("data_example").load_profile("6901774_112"),
    }

    plot_similar_comparison(name_profiles=name_profiles_ses, attr="DOXY", title=f"6901774_112")



