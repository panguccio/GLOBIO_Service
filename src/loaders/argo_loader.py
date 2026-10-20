from argopy import DataFetcher

def fetch_data(mode: str, params: list, region: list):
    # controllare se è da cambiare in data
    return DataFetcher(mode=mode, ds='bgc', params=params).region(region).to_xarray()