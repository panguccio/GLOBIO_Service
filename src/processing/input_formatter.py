import xarray as xr
import pandas as pd
import math
import torch
from datetime import datetime


def encode_sample(data: xr.Dataset, data_file: str, attributes: list):
    sample = {}

    sample["name"] = data_file
    sample["year"], sample["day"] = format_time(data)
    sample["space"] = format_space(data)
    sample["target_variable"] = None
    sample["device_name"] = None
    format_attributes(data_file, attributes, data, sample)


    return sample


class WmoDataset(torch.utils.data.Dataset):

    def __init__(self, data_files: set, attributes: list):
        self.dataset = []
        for data_file in data_files:
            data = xr.open_dataset(data_file)
            sample = encode_sample(data, data_file, attributes)
            self.dataset.append(sample)

    def __str__(self):
        if not self.dataset:
            return "WmoDataset (vuoto)"
        return f"WmoDataset(num_samples={len(self.dataset)})"

    def __getitem__(self, index):
        return self.dataset[index]

    def summary(self):
        """Prints a summary of the dataset and structure of the samples."""
        print(f"=== WmoDataset Summary ===")
        print(f"-> Sample number: {len(self.dataset)}")

        if not self.dataset:
            return

        for i, sample in enumerate(self.dataset):

            print(f"\n-> Sample no {i}:")
            for key, value in sample.items():
                if isinstance(value, torch.Tensor):
                    print(f"  - {key:<18} -> Tensor shape: {list(value.shape)}")
                else:
                    print(f"  - {key:<18} -> Valore: {value}")


# --- TIME ---
def format_time(data: xr.Dataset):
    try:
        date = pd.Timestamp(data['TIME'].values)
    except KeyError:
        date = data['REFERENCE_DATE_TIME'].values
        date = datetime.strptime(date.item().decode("utf-8"), "%Y%m%d%H%M%S")
        date = pd.Timestamp(date)

    print(date)
    year = date.year
    year_offset = (year - 2010)
    year = torch.tensor(year_offset)

    day_rad = 2 * math.pi * (date.dayofyear - 1) / 365
    day_sin = math.sin(day_rad)
    day_cos = math.cos(day_rad)
    day = torch.stack([torch.tensor(day_sin), torch.tensor(day_cos)])

    return year, day

# --- SPACE ---
def format_space(data: xr.Dataset):
    lat = float(data['LATITUDE'].values.squeeze())
    lon = float(data['LONGITUDE'].values.squeeze())
    x, y, z = encode_space(lat, lon)
    return torch.stack([x, y, z])

# --- ATTRIBUTES ---
def format_attributes(data_file: str, attributes: list, data: xr.Dataset, sample_dict: dict):
    label = 1

    for attribute in attributes:
        try:
            values = [float(d) for d in data[attribute]]
        except KeyError as e:
            print(data_file, e)
            continue
        values_tensor, label_value = from_list_to_tensor(values)
        label = label * label_value
        sample_dict[attribute.lower()] = values_tensor

        sample_dict["label"] = label


# --- UTILS ---
# WARNING: these methods need to be updated with more checks

def encode_space(lat, lon):
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)

        x = math.cos(lat_rad) * math.cos(lon_rad)
        y = math.cos(lat_rad) * math.sin(lon_rad)
        z = math.sin(lat_rad)

        return torch.tensor(x), torch.tensor(y), torch.tensor(z)

def from_list_to_tensor(profile_values: list):
    threshold = 99999
    label = 1
    out = torch.zeros(200)

    # se sono più di 200 i livelli che faccio? per adesso li taglio...
    for index in range(min(len(profile_values), 200)):
        value = profile_values[index]
        # if math.isnan(value): # DOMANDA: COSA FARE CON I VALORI NAN?
            # continue
        if float(value) >= threshold:
            label = 0
        out[index] = torch.tensor(value)
    return out, label

def normalize(x, name):
    pass
    norm_stats = []
    if norm_stats is not None and name in norm_stats:
        mean, std = norm_stats[name]
        return (x - mean) / std
    return x
