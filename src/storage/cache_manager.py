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

    def save_data(self, data, path):
        file_path = os.path.join(path, "test")
        try:
            data.to_netcdf(path=file_path, mode="w", format="NETCDF4")
        except Exception as e:
            print(e)
