from abc import abstractmethod

import argopy
from argopy import ArgoIndex, DataFetcher

class BaseArgoLoader():

    @abstractmethod
    def fetch_profiles(self, mode, params, region, backend):
        pass


class ArgopyLoader(BaseArgoLoader):

    def __init__(self):
        # 'bgc-s': profili BGC sintetici (Sprof), con tutti i parametri biogeochimici già raccolti
        # e interpolati sulla stessa griglia di pressione.
        # L’indice si può caricare una volta sola.
        self.idx = ArgoIndex(index_file="bgc-s")

    def get_index(self, box):
        # why does it not find query?
        self.idx.query.box(box)
        data_idx = self.idx.to_dataframe()
        # self.idx.to_indexfile("search_index.txt")
        return data_idx

    def idx_subset(self, wmos, cycles):
        self.idx.query.wmo_cyc(wmos, cycles)
        data_idx = self.idx.to_dataframe()
        return data_idx

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



