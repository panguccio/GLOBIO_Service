import xarray as xr
import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

_PROFILE_RE = re.compile(r"^S(?P<mode>[DR])(?P<wmo>\d+)_(?P<cycle>\d+)\.nc$")
_MODES = ("D", "R", "A")


class MemoryManager:
    """Class to save xr.Dataset profiles to netcdf files and to load them from memory."""
    def __init__(self, dir_name: str = "data_unlabeled"):
        self.base_dir = Path("data", dir_name)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def load_profiles(self) -> xr.Dataset | list[xr.Dataset] | None:
        """Loads the profiles from memory, concatenated along N_PROF.
        Returns:
            xr.Dataset -> the combined xr.Dataset
            list[xr.Dataset] -> if the concatenation fails
            None -> if no profiles are found
        """

        file_paths = self.get_profiles_paths()

        if not file_paths:
            logger.warning("Loading profiles failed: no profiles found.")
            return None

        logger.info(f"Loading {len(file_paths)} profiles from {self.base_dir}...")

        datasets = [self._read_profile(path) for path in file_paths]

        try:
            return xr.concat(
                datasets,
                dim='N_PROF',
                data_vars='minimal',
                coords='minimal',
                compat='override'
            )

        except Exception as e:
            logger.warning(f"Returned the list of datasets, instead of a single xr.Dataset.\nError during concatenation of datasets: {e}")
            return datasets

    def load_profile(self, wmo: int, cycle: int) -> xr.Dataset | None:
        """Loads a profile from a wmo+cycle couple, regardless of the mode (D/R)."""
        path = self._find_profile_path(wmo, cycle)
        if path is None:
            logger.warning(f"Profile {wmo}_{cycle} not found.")
            return None
        return self.load_profile_from_path(path)

    def load_profile_from_path(self, path: Path | str) -> xr.Dataset | None:
        """Loads a profile from an exact path."""
        path = Path(path)
        if not path.is_file():
            logger.warning(f"Loading profile failed: '{path}' does not exist.")
            return None
        try:
            return self._read_profile(path)
        except Exception as e:
            logger.error(f"Loading profile {path} failed: {e}")
            return None

    def save_profiles(self, profiles: xr.Dataset, replace: bool = True):
        """Saves the profiles in memory in the correct format."""
        if profiles is None:
            return

        n_profiles = profiles.sizes['N_PROF']
        logger.info(f"Saving {n_profiles} profiles...")

        for i in range(n_profiles):
            profile = profiles.isel(N_PROF=i)

            file_path = self._get_path_from_profile(profile)

            if file_path.is_file() and not replace:
                logger.info(f"{file_path} SKIPPED: already in memory.")
                continue

            file_path.parent.mkdir(parents=True, exist_ok=True)
            profile.to_netcdf(path=file_path, format="NETCDF4")
            logger.info(f"{file_path} SAVED.")

    def get_profiles_paths(self) -> list[Path]:
        """Scans the base dir and returns the set of paths."""
        return sorted([path for path in self.base_dir.glob("*/*.nc") if _PROFILE_RE.match(path.name)])

    def get_profiles_list(self) -> list[tuple[int, int]]:
        """Returns tuples wmo+cycle saved."""
        return [self.parse_profile_filename(path) for path in self.get_profiles_paths()]

    def _format_profile_path(self, mode: str, wmo: int, cycle: int) -> Path:
        """Returns complete path from mode, wmo, cycle."""
        return Path(self.base_dir, str(wmo), f"S{mode}{wmo}_{cycle:03d}.nc")

    def _find_profile_path(self, wmo: int, cycle: int) -> Path | None:
        """Finds the file of a profile, regardless of the mode (D/R)."""
        for mode in _MODES:
            path = self._format_profile_path(mode, wmo, cycle)
            if path.is_file():
                return path
        return None

    def _get_path_from_profile(self, profile: xr.Dataset) -> Path:
        """Returns complete path from profile."""
        mode = str(profile['DOXY_DATA_MODE'].values.item())
        if mode == "A": mode = "D"
        wmo = int(profile['PLATFORM_NUMBER'].values.item())
        cycle = int(profile['CYCLE_NUMBER'].values.item())
        return self._format_profile_path(mode, wmo, cycle)

    @staticmethod
    def _read_profile(file_path: Path) -> xr.Dataset:
        """Opens a profile."""
        with xr.open_dataset(file_path) as ds:
            return ds.load()

    @staticmethod
    def parse_profile_filename(filename: Path) -> tuple[int, int]:
        """Returns (wmo, cycle) from a profile file name."""
        match = _PROFILE_RE.match(filename.name)
        if match is None:
            raise ValueError(f"Invalid profile file name: {filename!r}")
        return int(match["wmo"]), int(match["cycle"])
