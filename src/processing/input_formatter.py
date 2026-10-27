import numpy as np
import xarray as xr



sample = {}
import pandas as pd
import math
import torch


def encode_sample(data):
    sample = {}

    sample["year"] = format_year(data)
    sample["day"] = format_day(data)
    sample["space"] = format_space(data)
    format_attributes(data, sample)
    sample["target_variable"] = None
    sample["device_name"] = None

    return sample


class WmoDataset(torch.utils.data.Dataset):

    def __init__(self, data_files: set):
        self.dataset = []
        for data_file in data_files:
            data = xr.open_dataset(data_file)
            sample = encode_sample(data)
            self.dataset.append(sample)

    def __getitem__(self, index):
        return self.dataset[index]


# --- TIME ---

def format_year(data):
    date = pd.Timestamp(data['TIME'].values)
    year = date.year
    year_offset = (year - 2010)
    return torch.tensor(year_offset)

def format_day(data):
    date = pd.Timestamp(data['TIME'].values)
    day_rad = 2 * math.pi * (date.dayofyear - 1) / 365
    day_sin = math.sin(day_rad)
    day_cos = math.cos(day_rad)
    return torch.stack([torch.tensor(day_sin), torch.tensor(day_cos)])

# --- SPACE ---
def format_space(data):
    lat = data['LATITUDE'].values
    lon = data['LONGITUDE'].values
    x, y, z = encode_space(lat, lon)
    return torch.stack([x, y, z])

# --- ATTRIBUTES ---
def format_attributes(data, sample_dict):
    label = 1

    for attribute in ['DOXY', 'PSAL', 'TEMP']:
        values = [float(d) for d in data[attribute]]
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
    for index in range(len(profile_values)):
        value = profile_values[index]
        if math.isnan(value): # DOMANDA: COSA FARE CON I VALORI NAN?
            continue
        if float(value) >= threshold:
            label = 0
        out[index] = torch.tensor(value)
    return out, label

def normalize(x, name):
    pass
    norm_stats = None
    if norm_stats is not None and name in norm_stats:
        mean, std = norm_stats[name]
        return (x - mean) / std
    return x
