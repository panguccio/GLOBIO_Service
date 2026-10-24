import os


def ensure_dir(directory: str):
    if not (os.path.exists(directory) and os.path.isdir(directory)):
        os.makedirs(directory)

def file_exists(file_path: str):
    return os.path.exists(file_path) and os.path.isfile(file_path)


class CacheManager:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir

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

