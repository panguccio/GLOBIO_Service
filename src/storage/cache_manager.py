import os


def ensure_dir(directory: str):
    if not (os.path.exists(directory) and os.path.isdir(directory)):
        os.makedirs(directory)

def file_exists(file_path: str):
    return os.path.exists(file_path) and os.path.isfile(file_path)


class CacheManager:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir

    def check_cache(self, target_files: list):
        existing_files = []
        for (root, dirs, files) in os.walk('data'):
            for file in files:
                existing_files.append(file)


        wmo_to_download = [wmo for wmo in target_files if wmo not in existing_files]

        wmos = [file_name.split("_")[0][2:] for file_name in wmo_to_download]
        cycles = [file_name.split("_")[1].split(".")[0][:3] for file_name in wmo_to_download]

        return wmos, cycles

    def save_data(self, profiles):
        n_profiles = profiles.sizes['N_PROF']

        if not (os.path.exists(self.base_dir) and os.path.isdir(self.base_dir)):
            os.makedirs(self.base_dir)

        for i in range(n_profiles):

            profile = profiles.isel(N_PROF=i)
            wmo = profile['PLATFORM_NUMBER'].values.item()
            cycle = profile['CYCLE_NUMBER'].values.item()

            folder = os.path.join(self.base_dir, str(wmo))
            ensure_dir(folder)

            # every cycle of a platform is a separate netcdf file in the corresponding wmo folder
            file_path = os.path.join(folder, f"SD{wmo}_{f"{cycle:03d}"}.nc")

            if file_exists(file_path):
                print(f"{file_path} already in memory.")
                continue

            print(f"Saving in {file_path}")

            # if the format is wrong, this method has to change

            profile.to_netcdf(path=file_path, format="NETCDF4")

