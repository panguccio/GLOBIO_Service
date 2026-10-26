import os


def ensure_dir(directory: str):
    if not (os.path.exists(directory) and os.path.isdir(directory)):
        os.makedirs(directory)

def file_exists(file_path: str):
    return os.path.exists(file_path) and os.path.isfile(file_path)


class CacheManager:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        ensure_dir(self.base_dir)

    def get_existing_profiles(self) -> set:
        """Scans the base dir and returns the set of (wmo, cyc) tuples already in memory."""
        existing = set()
        if not os.path.exists(self.base_dir):
            return existing

        for wmo_dir in os.listdir(self.base_dir):
            wmo_path = os.path.join(self.base_dir, wmo_dir)
            if os.path.isdir(wmo_path):
                for file in os.listdir(wmo_path):
                    if file.endswith(".nc"):
                        try:
                            # Name file example: SD5901234_001.nc
                            parts = file.split("_")
                            wmo = parts[0][2:]  # Rimuove 'SD'
                            cycle = int(parts[1].split(".")[0])
                            existing.add((str(wmo), int(cycle)))
                        except Exception:
                            continue
        return existing

        wmo_to_download = [wmo for wmo in target_files if wmo not in existing_files]

        wmos = [file_name.split("_")[0][2:] for file_name in wmo_to_download]
        cycles = [file_name.split("_")[1].split(".")[0][:3] for file_name in wmo_to_download]

        return wmos, cycles

    def save_data(self, profiles):
        """Saves the profiles in memory in the correct format."""
        if profiles is None:
            return

        n_profiles = profiles.sizes['N_PROF']

        if not (os.path.exists(self.base_dir) and os.path.isdir(self.base_dir)):
            os.makedirs(self.base_dir)

        for i in range(n_profiles):

            profile = profiles.isel(N_PROF=i)
            wmo = str(profile['PLATFORM_NUMBER'].values.item())
            cycle = int(profile['CYCLE_NUMBER'].values.item())

            folder = os.path.join(self.base_dir, wmo)
            ensure_dir(folder)

            file_path = os.path.join(folder, f"SD{wmo}_{cycle:03d}.nc")

            if file_exists(file_path):
                continue

            print(f"Saving: {file_path}")
            profile.to_netcdf(path=file_path, format="NETCDF4")