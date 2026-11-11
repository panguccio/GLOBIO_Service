import os
import xarray as xr
import re
from pathlib import Path

_PROFILE_RE = re.compile(r"^S(?P<mode>[DR])(?P<wmo>\d+)_(?P<cycle>\d+)\.nc$")
_MODES = ("D", "R")

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

def parse_profile_filename(filename: str) -> tuple[int, int]:
    """Returns (wmo, cycle) from a profile file name. Raises ValueError if invalid."""
    match = _PROFILE_RE.match(Path(filename).name)
    if match is None:
        raise ValueError(f"Invalid profile file name: {filename!r}")
    return match["wmo"], int(match["cycle"])

def format_profile_filename(mode: str, wmo: int, cycle: int) -> str:
    return f"S{mode}{wmo}_{int(cycle):03d}.nc"

class MemoryManager:
    def __init__(self, dir_name: str = "data_unlabeled"):

        self.base_dir = os.path.join("data", dir_name)
        ensure_dir(self.base_dir)

    def get_profiles_paths(self) -> set:
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

    def load_profiles(self):
        """Loads the profiles from memory, transforming netcdf files into a xarray.Dataset.
        If it fails, it returns the dictionary with all the profiles."""

        file_paths = list(self.get_profiles_paths())

        if not file_paths:
            print('Loading profiles failed: no profiles found.')
            return None

        print(f'Loading {len(file_paths)} profiles from memory...')

        datasets = []

        for file_path in file_paths:
            with xr.open_dataset(file_path) as ds:
                profile = ds.load()
            datasets.append(profile)

        try:
            ds_combined = xr.concat(
                datasets,
                dim='N_PROF',
                data_vars='minimal',
                coords='minimal',
                compat='override'
            )
            for ds in datasets:
                ds.close()
            return ds_combined

        except Exception as e:
            print(f"Error during concatenation of datasets: {e}")
            return datasets

    def _find_profile_path(self, wmo, cycle):
        """Finds the file of a profile, regardless of the mode (D/R)."""
        for mode in ["D", "R"]:
            path = os.path.join(self.base_dir, str(wmo), f"S{mode}{wmo}_{int(cycle):03d}.nc")
            if file_exists(path):
                return path
        return None

    def load_profile(self, wmo, cycle):
        """Loads a profile from a wmo+cycle couple, regardless of the mode (D/R)."""
        path = self._find_profile_path(wmo, cycle)
        if path is None:
            print(f"Profile {wmo}_{cycle} not found.")
            return None
        return self.load_profile_from_path(path)

    @staticmethod
    def load_profile_from_path(path):
        """Carica un profilo da un path esatto."""
        if not file_exists(path):
            print(f"Loading profile failed: '{path}' does not exist.")
            return None
        try:
            with xr.open_dataset(path) as ds:
                return ds.load()
        except Exception as e:
            print(f"Loading profile {path} failed: {e}")
            return None

    def save_profiles(self, profiles, replace=True):
        """Saves the profiles in memory in the correct format."""
        if profiles is None:
            return

        n_profiles = profiles.sizes['N_PROF']
        print(f"Saving {n_profiles} profiles...")

        for i in range(n_profiles):
            profile = profiles.isel(N_PROF=i)
            mode = str(profile['DOXY_DATA_MODE'].values.item())
            if mode == "A": mode = "D"
            wmo = str(profile['PLATFORM_NUMBER'].values.item())
            cycle = int(profile['CYCLE_NUMBER'].values.item())

            folder = os.path.join(self.base_dir, wmo)
            ensure_dir(folder)

            file_path = os.path.join(folder, f"S{mode}{wmo}_{cycle:03d}.nc")

            if file_exists(file_path) and not replace:
                print(f"{file_path} SKIPPED: already in memory.")
                continue

            print(f"{file_path} SAVED.")
            profile.to_netcdf(path=file_path, format="NETCDF4")


