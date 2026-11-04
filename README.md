# GLOBIO Twin Service

Python project for downloading and preparing Argo BGC oceanographic profiles. The current workflow uses [argopy](https://argopy.readthedocs.io/) to retrieve profiles, converts them to a standardized NetCDF format, and provides tools to load them as PyTorch datasets and compare them visually.

## Features

- Querying the Argo BGC index and downloading profiles in `standard` or `expert` mode.
- Converting dissolved oxygen concentrations from µmol/kg to mmol/m³ using density calculated with `gsw`.
- Formatting profiles as an xarray dataset and saving them to NetCDF files organized by WMO and cycle.
- Loading profiles into a PyTorch dataset (`WmoDataset`).
- Plotting profile comparisons and differences.


## Installazione

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```


## Project structure

```text
src/
├── main.py                    # Workflow coordination functions
├── main.ipynb                 # Interactive examples and comparisons
├── loaders/argo_loader.py     # Argo downloads and queries via argopy
├── processing/
│   ├── conversions.py         # Concentration conversions
│   ├── input_formatter.py     # PyTorch dataset and profile encoding
│   └── netcdf_formatter.py    # Conversion to the standard NetCDF format
├── storage/cache_manager.py   # Reading and writing NetCDF profiles
├── graphics/plotter.py        # Comparison plots
└── models/                    # Available model weights
```

Downloaded data and generated plots are stored locally and are not included among the project's tracked files. `src/models/` contains the `chla_model.pt` and `nitrate_model.pt` weights.
