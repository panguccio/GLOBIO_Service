import pandas as pd
import xarray as xr
import numpy as np

def format_date(times):
    """Format dates as an array of: YYYYMMDDHHMMSS"""

    if np.isscalar(times):
        times = [times]
    datetime_str_list = []
    for t in times:
        dt_str = pd.Timestamp(t).strftime('%Y%m%d%H%M%S')
        datetime_str_list.append(list(dt_str))
    datetime_arr = np.array(datetime_str_list, dtype='S1')
    return datetime_arr

def convert_argo_to_standard(ds_argo, metadata=None):
    """Converts argopy xarray in standard OGS format.
    """

    n_prof = ds_argo.sizes['N_PROF']

    times = ds_argo['TIME'].values
    datetime_arr = format_date(times)
    wmo = ds_argo['PLATFORM_NUMBER'].values.astype(np.int64)
    cycle = ds_argo['CYCLE_NUMBER'].values.astype(np.int64)
    lons = ds_argo['LONGITUDE'].values.astype(np.float64)
    lats = ds_argo['LATITUDE'].values.astype(np.float64)
    data_mode = ds_argo['DOXY_DATA_MODE'].values

    ds_out = xr.Dataset(
        data_vars={
            # --- Coordinates ---
            'CYCLE_NUMBER': (
                ('N_PROF',),
                cycle,
                {'variable': 'CYCLE', 'units': 'int'},
            ),
            'PLATFORM_NUMBER': (
                ('N_PROF',),
                wmo,
                {'variable': 'WMO', 'units': 'int'},
            ),

            'TIME': (('N_PROF',), times),
            'REFERENCE_DATE_TIME': (('N_PROF', 'DATETIME'), datetime_arr),

            'LONGITUDE': (('N_PROF',), lons),
            'LATITUDE': (('N_PROF',), lats),

            'DOXY_DATA_MODE': (('N_PROF',), data_mode),

            # --- DOXY ---
            'DOXY': (
                ('N_PROF', 'nDOXY'),
                ds_argo['DOXY'].values,
                {'variable': 'DOXY', 'units': 'mmol/m3'},
            ),
            'PRES_DOXY': (
                ('N_PROF', 'nDOXY'),
                ds_argo['PRES'].values,
            ),

            # --- TEMP ---
            'TEMP': (
                ('N_PROF', 'nTEMP'),
                ds_argo['TEMP'].values,
                {'variable': 'TEMP', 'units': 'degree_Celsius'},
            ),
            'PRES_TEMP': (
                ('N_PROF', 'nTEMP'),
                ds_argo['PRES'].values,
            ),

            # --- PSAL ---
            'PSAL': (
                ('N_PROF', 'nPSAL'),
                ds_argo['PSAL'].values,
                {'variable': 'SALI', 'units': 'PSS78'},
            ),
            'PRES_PSAL': (('N_PROF', 'nPSAL'), ds_argo['PRES'].values),

            # --- CHLA ---
            'CHLA': (
                ('N_PROF', 'nCHLA'),
                ds_argo['CHLA'].values
                if 'CHLA' in ds_argo
                else np.full(ds_argo['TEMP'].shape, np.nan),
                {'variable': 'CHLA', 'units': 'mmol/m3'},
            ),
            'PRES_CHLA': (
                ('N_PROF', 'nCHLA'),
                ds_argo['PRES'].values,
            ),

            # --- NITRATE ---
            'NITRATE': (
                ('N_PROF', 'nNITRATE'),
                ds_argo['NITRATE'].values
                if 'NITRATE' in ds_argo
                else np.full(ds_argo['TEMP'].shape, np.nan),
                {'variable': 'NITRATE', 'units': 'mmol/m3'},
            ),
            'PRES_NITRATE': (
                ('N_PROF', 'nNITRATE'),
                ds_argo['PRES'].values,
            ),

        },
        coords={
            'N_PROF': np.arange(n_prof),
            'nDOXY': ds_argo['N_LEVELS'].values,
            'nTEMP': ds_argo['N_LEVELS'].values,
            'nPSAL': ds_argo['N_LEVELS'].values,
            'nCHLA': ds_argo['N_LEVELS'].values,
            'nNITRATE': ds_argo['N_LEVELS'].values,
            'DATETIME': np.arange(14),
        },
        attrs={
            'origin': 'argopy',
            'file_origin': getattr(metadata, 'filename', 'argopy_fetch'),
        },
    )

    return ds_out
