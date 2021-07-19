# Script to Load MUR SST Anomaly Data
# Matthew Thompson

# Import modules
import s3fs
import numpy as np
import xarray as xr
import fsspec
import zarr
import matplotlib.pyplot as plt
from dask.distributed import Client

# Dataset URL
URL = 's3://mur-sst/zarr'

# Region of interest
minlat = 18
maxlat = 25
minlon = -160
maxlon = -150

# Checkpoint tag
print("Opening MUR SST zarr data stored in AWS")

# Open dataset
ds = xr.open_zarr(fsspec.get_mapper(URL, anon=True), consolidated=True)

# Define dates to iterate through
start_dates = []
end_dates = []
for date in range(2, 21):
    if (date == 2):
        start_dates.append("2002-06-01T09:00:00")
        end_dates.append("200" + str(date) + "-12-31T09:00:00")
    elif (date == 20):
        start_dates.append("20" + str(date) + "-01-01T09:00:00")
        end_dates.append("2020-01-20T09:00:00")
    elif (len(str(date)) == 1):
        start_dates.append("200" + str(date) + "-01-01T09:00:00")
        end_dates.append("200" + str(date) + "-12-31T09:00:00")
    else:
        start_dates.append("20" + str(date) + "-01-01T09:00:00")
        end_dates.append("20" + str(date) + "-12-31T09:00:00")

# Checkpoint tag
print("Beginning to load dataset")

# Loop to iterate through each year in the dataset
for year in range(0, len(start_dates)):

    # Checkpoint tag
    print("Loading dataset for start date: " + start_dates[year])

    # Set start and end dates for this iteration
    start_date = np.datetime64(start_dates[year], 'ns')
    end_date = np.datetime64(end_dates[year], 'ns')

    # Slice dataset to create subset
    variables=[
        'analysed_sst', 
        'mask'
    ]
    mur_L4_subset = ds[variables].sel(
        time=slice(start_date, end_date),
        lat=slice(minlat, maxlat), 
        lon=slice(minlon, maxlon),
    ).chunk({"time": 30, "lat": 100, "lon": 100})

    # Add in NAN values for land to MUR data
    mur_L4_subset_no_land = mur_L4_subset['analysed_sst'].where(mur_L4_subset.mask == 1)

    # Convert temperatures to celsius
    mur_subset_final = mur_L4_subset_no_land - 273.15

    # Load in MUR climatology
    mur_clim = xr.open_dataarray(
        "../data/MURClimatology.nc", 
        chunks={"time": 30, "lat": 100, "lon": 100}
    )

    # Dropping Leap Day
    if mur_subset_final["time"].size <= 365:
        mur_clim = mur_clim.where(mur_clim["time"] != np.datetime64('2004-02-29T09:00:00', 'ns'), drop=True)

    # Take subset of MUR climatology for incomplete years
    # 2002
    if (mur_subset_final["time"][0].values == np.datetime64('2002-06-01T09:00:00', 'ns')):
        mur_clim = mur_clim[151:]

    # 2020
    if (mur_subset_final["time"][0].values == np.datetime64('2020-01-01T09:00:00', 'ns')):
        mur_clim = mur_clim[:20]

    # Assign correct time values to MUR climatology
    mur_clim = mur_clim.assign_coords({"time": mur_subset_final["time"]})

    # Subtract climatology from average MUR SST
    sst_anomaly_concat = mur_subset_final - mur_clim

    # Add attributes to dataset
    sst_anomaly_concat.attrs = {
        "description" : "Hawaii sea surface temperature anomalies",
        "start_date" : "2002-06-01",
        "end_date" :"2020-01-20",
        "units" : "degC",
    }

    # Concatenate all years into one dataset
    if (sst_anomaly_concat["time"][0].values == np.datetime64('2002-06-01T09:00:00', 'ns')):
        sst_anomaly = sst_anomaly_concat
    else:
        sst_anomaly = xr.concat([sst_anomaly, sst_anomaly_concat], dim="time")
    
# Checkpoint tag
print("Dataset loaded")

# Rechunk dataset 
sst_anomaly = sst_anomaly.chunk({"time": 30, "lat": 100, "lon": 100})

# Figure out averaging over region
sst_anomaly_mean = sst_anomaly.mean(['lat', 'lon'])

# Checkpoint tag
print("Plotting mean SST Anomaly over region")

# Plot the mean values over the region, save to file
fig1, ax1 = plt.subplots()
sst_anomaly_mean.plot(ax=ax1)
fig1.savefig("../data/MURSSTAnomalyMeanRegion.pdf")

# Checkpoint tag
print("Plotting SST Anomaly at specific location")

# Plot the values over a specific coordinate pair, save to file
fig2, ax2 = plt.subplots()
sst_anomaly.isel(lat=350, lon=500).plot(ax=ax2)
fig2.savefig("../data/MURSSTAnomalyLocation.pdf")

# Download the MUR SST anomaly data to netCDF4
sst_anomaly_mean.to_netcdf("../data/MURSSTAnomalyMean.nc")

# Download the MUR SST anomaly data to zarr
# sst_anomaly_ds = sst_anomaly.to_dataset(name= "sst_anomaly", promote_attrs=True)
# sst_anomaly_ds.to_zarr("../data/MURSSTAnomaly2002.zarr", mode="w", consolidated=True)
# sst_anomaly_test = xr.open_dataarray("../data/MURSSTAnomaly2002.zarr")