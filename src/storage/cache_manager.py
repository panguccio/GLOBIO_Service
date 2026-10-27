import os


def ensure_dir(directory: str):
    if not (os.path.exists(directory) and os.path.isdir(directory)):
        os.makedirs(directory)

def file_exists(file_path: str):
    return os.path.exists(file_path) and os.path.isfile(file_path)


def deformat_path(file):
    # Name file example: SD5901234_001.nc
    parts = file.split("_")
    wmo = parts[0][2:]  # Rimuove 'SD'
    cycle = int(parts[1].split(".")[0])
    return wmo, cycle


class MemoryManager:
    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir
        ensure_dir(self.base_dir)

    def get_existing_profiles(self) -> set:
        """Scans the base dir and returns the set of paths."""
        existing = set()
        if not os.path.exists(self.base_dir):
            return existing

        for wmo_dir in os.listdir(self.base_dir):
            wmo_path = os.path.join(self.base_dir, wmo_dir)
            if os.path.isdir(wmo_path):
                for file in os.listdir(wmo_path):
                    if file.endswith(".nc"):
                        try:
                            wmo, cycle = deformat_path(file)
                            existing.add(os.path.join(wmo_path, file))
                        except Exception:
                            continue
        return existing

    def save_netcdf(self, profiles):
        """Saves the profiles in memory in the correct format."""
        if profiles is None:
            return

        n_profiles = profiles.sizes['N_PROF']
        print(f"Saving {n_profiles} profiles...")

        for i in range(n_profiles):
            profile = profiles.isel(N_PROF=i)
            wmo = str(profile['PLATFORM_NUMBER'].values.item())
            cycle = int(profile['CYCLE_NUMBER'].values.item())

            folder = os.path.join(self.base_dir, wmo)
            ensure_dir(folder)

            file_path = os.path.join(folder, f"SD{wmo}_{cycle:03d}.nc")

            if file_exists(file_path):
                print(f"{file_path} already in memory.")
                continue

            print(f"Saving: {file_path}")
            profile.to_netcdf(path=file_path, format="NETCDF4")


