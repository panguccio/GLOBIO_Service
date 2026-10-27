import xarray as xr
import pandas as pd
import math
import torch
from datetime import datetime


def encode_sample(data: xr.Dataset):
    sample = {}

    sample["year"], sample["day"] = format_time(data)
    sample["space"] = format_space(data)
    format_attributes(['DOXY', 'PSAL', 'TEMP'], data, sample)
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

    def __str__(self):
        if not self.dataset:
            return "WmoDataset (vuoto)"

        num_samples = len(self.dataset)
        sample_keys = list(self.dataset[0].keys())

        # Separiamo i metadati generali dai tensori dei profili (200 livelli)
        profile_keys = ['doxy', 'psal', 'temp']
        meta_keys = [k for k in sample_keys if k not in profile_keys]

        output = []
        output.append("=" * 80)
        output.append(" WMO DATASET SUMMARY (Metadata per Sample)")
        output.append("=" * 80)

        # 1. Tabella dei Metadati (campi scalari o vettori brevi)
        col_width = 22
        header = f"{'Metadata':<18}"
        for i in range(num_samples):
            header += f" | S{i:<{col_width}}"
        output.append(header)
        output.append("-" * len(header))

        for key in meta_keys:
            row = f"{key:<18}"
            for sample in self.dataset:
                val = sample.get(key, "N/A")
                if isinstance(val, torch.Tensor):
                    if val.numel() == 1:
                        val_str = f"{val.item():.4g}"
                    else:
                        # Mostra una forma compatta per vettori brevi (es. space o day)
                        val_str = str([round(x.item(), 3) for x in val])
                        if len(val_str) > col_width:
                            val_str = val_str[:col_width - 3] + "..."
                elif val is None:
                    val_str = "None"
                else:
                    val_str = str(val)
                row += f" | {val_str:<{col_width}}"
            output.append(row)

        output.append("\n")

        # 2. Tabelle Verticali per i Profili (Righe = Livelli 0-199, Colonne = Sample)
        for p_key in profile_keys:
            if p_key not in sample_keys:
                continue

            output.append("=" * 80)
            output.append(f" PROFILO VERTICALE: {p_key.upper()} (Confronto per Livello)")
            output.append("=" * 80)

            p_col_width = 15
            p_header = f"{'Level':<8}"
            for i in range(num_samples):
                p_header += f" | S{i:<{p_col_width}}"
            output.append(p_header)
            output.append("-" * len(p_header))

            # Scorriamo tutti i 200 livelli
            max_len = 200
            for level_idx in range(max_len):
                row = f"{level_idx:<8}"
                for sample in self.dataset:
                    tensor_val = sample.get(p_key)
                    if isinstance(tensor_val, torch.Tensor) and level_idx < len(tensor_val):
                        val_item = tensor_val[level_idx].item()
                        val_str = f"{val_item:.4g}"
                    else:
                        val_str = "N/A"
                    row += f" | {val_str:<{p_col_width}}"
                output.append(row)
            output.append("\n")

        return "\n".join(output)

    def __getitem__(self, index):
        return self.dataset[index]


# --- TIME ---
def format_time(data: xr.Dataset):
    try:
        date = pd.Timestamp(data['TIME'].values)
    except KeyError:
        date = data['REFERENCE_DATE_TIME'].values
        date = datetime.strptime(date.item().decode("utf-8"), "%Y%m%d%H%M%S")
        date = pd.Timestamp(date)

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
def format_attributes(attributes: list, data: xr.Dataset, sample_dict: dict):
    label = 1

    for attribute in attributes:
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
