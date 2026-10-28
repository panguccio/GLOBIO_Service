import gsw
import xarray as xr

def convert_mmol(data):
    # method to convert doxy and nitrate from micromole/Kg to mmol/m3
    ds = data.copy()

    # aligns all variables with the same dimensions.
    psal, pres, lon, lat, temp = xr.broadcast(
        ds['PSAL'], ds['PRES'], ds['LONGITUDE'], ds['LATITUDE'], ds['TEMP']
    )

    sa = gsw.SA_from_SP(psal.values, pres.values, lon.values, lat.values)
    ct = gsw.CT_from_t(sa, temp.values, pres.values)
    density = gsw.rho(sa, ct, pres.values)

    ds['DOXY'] = ds['DOXY'] * density / 1000

    try:
        ds['NITRATE'] = ds['NITRATE'] * density / 1000
    except KeyError:
        pass

    try:
        ds['CHLA'] = ds['CHLA'] * density / 1000
    except KeyError:
        pass

    return ds