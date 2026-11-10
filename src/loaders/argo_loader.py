from abc import abstractmethod, ABC
from dataclasses import dataclass, replace
from typing import Sequence
import xarray as xr
from argopy import ArgoIndex, DataFetcher
from enum import Enum
import argopy

class Backend(str, Enum):
    PYARROW = "pyarrow"
    PANDAS = "pandas"

@dataclass(frozen=True)
class Config:
    params: tuple[str, ...] = ("DOXY",)
    mode: str = "standard"
    backend: Backend = Backend.PYARROW
    cache: bool = True

class BaseArgoLoader(ABC):
    """Common interface for all Argo loaders"""
    def __init__(self, config: Config | None = None):
        self.config = config if config is not None else Config()

    def _set_config(self, config: Config | None = None, **overrides) -> Config:
        return replace(config if config is not None else self.config, **overrides)

    @abstractmethod
    def fetch_profiles(self, region: Sequence[float], config: Config | None = None, **overrides) -> xr.Dataset:
        ...
    @abstractmethod
    def fetch_profile(self, wmo: int, cycle: int, config: Config | None = None, **overrides) -> xr.Dataset:
        ...

class ArgopyLoader(BaseArgoLoader):
    DATASET = "bgc"
    INDEX_FILE = "bgc-s"

    def __init__(self, config: Config | None = None, cache_dir: str = "data/argopy-cache", clear_cache: bool = False):
        super().__init__(config)
        self._argopy_config(cache_dir, clear_cache)
        self.idx = ArgoIndex(index_file=self.INDEX_FILE)
        self.idx.load()

    @staticmethod
    def _argopy_config(cache_dir, clear_cache):
        argopy.reset_options()
        if clear_cache:
            argopy.clear_cache()
        argopy.set_options(cachedir=cache_dir)

    def _build_fetcher(self, cfg: Config) -> DataFetcher:
        try:
            backend = Backend(cfg.backend)
        except ValueError:
            valid = ", ".join(b.value for b in Backend)
            raise NotImplementedError(f"Backend {cfg.backend} not implemented. Did you mean {valid}?") from None

        kwargs = dict(mode=cfg.mode, params=list(cfg.params), cache=cfg.cache, ds=self.DATASET, parallel=True)
        if backend == Backend.PYARROW:
            kwargs["indexfs"] = self.idx
        return DataFetcher(**kwargs)

    def get_index_box(self, box):
        """Returns the dataframe for the box-area of interest."""
        self.idx.query.box(box)
        return self.idx.to_dataframe()

    def fetch_profiles(self, region, config: Config | None = None, **overrides):
        cfg = self._set_config(config, **overrides)
        fetcher = self._build_fetcher(cfg).region(list(region))
        fetcher.load()
        return fetcher.data.argo.point2profile()

    def fetch_profile(self, wmo, cycle, config: Config | None = None, **overrides):
        cfg = self._set_config(config, **overrides)
        fetcher = self._build_fetcher(cfg).profile(wmo, cycle)
        fetcher.load()
        return fetcher.data




