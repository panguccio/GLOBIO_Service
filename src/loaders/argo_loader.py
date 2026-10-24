import argopy
from argopy import ArgoIndex, DataFetcher



def fetch_profiles(mode: str, params: list, region: list):

    # 'bgc-s': profili BGC sintetici (Sprof), con tutti i parametri biogeochimici già raccolti
    # e interpolati sulla stessa griglia di pressione.
    # L’indice si può caricare una volta sola.
    idx = ArgoIndex(index_file="bgc-s")
    df = DataFetcher(mode=mode, ds='bgc', params=params, indexfs=idx, parallel=True).region(region)
    df.load()
    data = df.data
    profiles = data.argo.point2profile()
    return profiles



