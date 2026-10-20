import gsw

def convert_unit(data):
    # from micromol/Kg to  mmol/m3
    ds = data.copy()
    SA = gsw.SA_from_SP(ds['PSAL'].values, ds['PRES'].values, ds['LONGITUDE'].values, ds['LATITUDE'].values)
    density = gsw.rho(SA, gsw.CT_from_t(SA, ds['TEMP'].values, ds['PRES'].values), ds['PRES'].values)

    ds['DOXY'] = ds['DOXY'] * density / 1000
    ds['NITRATE'] = ds['NITRATE'] * density / 1000

    return ds


def to_superfloat(data):
    pass