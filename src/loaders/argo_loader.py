from abc import abstractmethod

import argopy
from argopy import ArgoIndex, DataFetcher

class BaseArgoLoader():

    @abstractmethod
    def fetch_profiles(self, mode, params, region, backend):
        pass


class ArgopyLoader(BaseArgoLoader):

    def __init__(self):

        # Argopy fresh start
        import argopy
        argopy.reset_options()
        argopy.clear_cache()
        argopy.set_options(cachedir='argopy-cache')

        # Initialization of the index
        self.idx = ArgoIndex(index_file="bgc-s")
        self.idx.load()

    def get_index_box(self, box):
        """Returns the dataframe for the box-area of interest."""
        self.idx.query.box(box)
        return self.idx.to_dataframe()

    def fetch_profiles(self, params: list, region: list, mode: str = "standard", backend: str = "pyarrow"):
        if backend == "pyarrow":
            df = DataFetcher(mode=mode, ds='bgc', params=params, indexfs=self.idx, parallel=True).region(region)
        elif backend == "pandas":
            df = DataFetcher(mode=mode, ds='bgc', params=params, parallel=True).region(region)
        else:
            raise NotImplementedError
        print("Downloading profiles... This might take a while...")
        df.load()
        data = df.data
        profiles = data.argo.point2profile()
        return profiles



