import os


class CacheManager:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir

    def dir_exists(self, start_date: str, end_date: str) -> bool:
        directory = os.path.join(self.base_dir, '_'.join([start_date, end_date]))
        return os.path.exists(directory) and os.path.isdir(directory)

    def create_dir(self, start_date: str, end_date: str):
        directory = os.path.join(self.base_dir, '_'.join([start_date, end_date]))
        if not self.dir_exists(start_date, end_date):
            os.makedirs(directory, exist_ok=False)
        return directory

    def save_data(self, profiles, path):
        n_profiles = profiles.sizes['N_PROF']

        if not (os.path.exists(path) and os.path.isdir(path)):
            os.makedirs(path)

        for i in range(n_profiles):
            profile = profiles.isel(N_PROF=i)
            wmo = profile['PLATFORM_NUMBER'].values.item()
            cycle = profile['CYCLE_NUMBER'].values.item()

            folder = os.path.join(path, str(wmo))

            # every cycle of a platform is a separate netcdf file in the corresponding wmo folder
            file_path = os.path.join(folder, f"SD{wmo}_{f"{cycle:03d}"}.nc")

            print(f"Saving in {file_path}")

            # if the format is wrong, this method has to change
            profile.to_netcdf(path=file_path, format="NETCDF4")

