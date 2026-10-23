import netCDF4 as NC

def save_profile_to_netcdf(self, filepath: str, ds_profile: xr.Dataset, metadata=None):
    """
    Salva un profilo xarray di argopy nel formato NetCDF desiderato.
    (La logica di dumpfile che hai scritto tu)
    """
    print(f"Dumping data on {filepath}", flush=True)

    lat = ds_profile['LATITUDE'].values
    lon = ds_profile['LONGITUDE'].values
    time = ds_profile['TIME'].values[0] if 'TIME' in ds_profile else np.datetime64('NaT')

    temp = ds_profile['TEMP'].values.squeeze()
    pres_t = ds_profile['PRES'].values.squeeze()
    qc_t = ds_profile['TEMP_QC'].values.squeeze() if 'TEMP_QC' in ds_profile else np.zeros_like(temp)

    sali = ds_profile['PSAL'].values.squeeze()
    qc_s = ds_profile['PSAL_QC'].values.squeeze() if 'PSAL_QC' in ds_profile else np.zeros_like(sali)

    chla = ds_profile['CHLA'].values.squeeze() if 'CHLA' in ds_profile else np.array([])
    pres_chla = ds_profile['PRES'].values.squeeze() if 'CHLA' in ds_profile else np.array([])
    qc_chla = ds_profile['CHLA_QC'].values.squeeze() if 'CHLA_QC' in ds_profile else np.zeros_like(chla)

    with NC.Dataset(filepath, "w") as ncOUT:
        setattr(ncOUT, 'origin', 'coriolis')
        setattr(ncOUT, 'file_origin', getattr(metadata, 'filename', 'argopy_dataset'))

        ncOUT.createDimension("DATETIME", 14)
        ncOUT.createDimension("NPROF", 1)
        ncOUT.createDimension('nTEMP', len(temp))
        ncOUT.createDimension('nPSAL', len(sali))
        ncOUT.createDimension('nCHLA', len(chla))

        ncvar = ncOUT.createVariable("REFERENCE_DATE_TIME", 'c', ("DATETIME",))
        time_str = np.datetime_as_string(time, unit='s').replace('-', '').replace(':', '').replace('T', '')[:14]
        ncvar[:] = list(time_str.ljust(14, '0'))

        ncvar = ncOUT.createVariable("JULD", 'd', ("NPROF",))
        ncvar[:] = 0.0

        ncvar = ncOUT.createVariable("LONGITUDE", "d", ("NPROF",))
        ncvar[:] = float(lon)

        ncvar = ncOUT.createVariable("LATITUDE", "d", ("NPROF",))
        ncvar[:] = float(lat)

        # TEMP
        ncvar = ncOUT.createVariable('TEMP', 'f', ('nTEMP',))
        ncvar[:] = temp
        setattr(ncvar, 'variable', 'TEMP')
        setattr(ncvar, 'units', "degree_Celsius")

        ncvar = ncOUT.createVariable('PRES_TEMP', 'f', ('nTEMP',))
        ncvar[:] = pres_t
        ncvar = ncOUT.createVariable('TEMP_QC', 'f', ('nTEMP',))
        ncvar[:] = qc_t

        # PSAL
        ncvar = ncOUT.createVariable('PSAL', 'f', ('nPSAL',))
        ncvar[:] = sali
        setattr(ncvar, 'variable', 'SALI')
        setattr(ncvar, 'units', "PSS78")

        ncvar = ncOUT.createVariable('PRES_PSAL', 'f', ('nPSAL',))
        ncvar[:] = pres_t
        ncvar = ncOUT.createVariable('PSAL_QC', 'f', ('nPSAL',))
        ncvar[:] = qc_s

        # CHLA
        if len(chla) > 0:
            ncvar = ncOUT.createVariable('CHLA', 'f', ('nCHLA',))
            ncvar[:] = chla
            setattr(ncvar, 'status_var', getattr(metadata, 'status_var', 'unknown'))
            setattr(ncvar, 'shift_from_coriolis', str(getattr(metadata, 'shift_from_coriolis', '')))
            setattr(ncvar, 'variable', 'CHLA_ADJUSTED')
            setattr(ncvar, 'units', "milligram/m3")

            ncvar = ncOUT.createVariable('PRES_CHLA', 'f', ('nCHLA',))
            ncvar[:] = pres_chla
            ncvar = ncOUT.createVariable('CHLA_QC', 'f', ('nCHLA',))
            ncvar[:] = qc_chla