# Cloud Analysis Runtime Comparison Between Native and Cloud-Optimized Data Formats

The goal of this project is to use a proxy “big data” dataset, in this case the MUR 1-km Sea Surface Temperature dataset, to compare runtimes between native (netCDF4) and cloud-optimized (Zarr) formats across several analysis scenarios.

## Goals
To compare MUR 1-km SST dataset in... 
- netCDF4
  - THREDDS, local analysis after downloading data
  - OPeNDAP On-Premise, local analysis after downloading data
  - Earthdata Search, local analysis after downloading data
  - Amazon Web Services (AWS) (computing), Earthdata Cloud (accessing dataset), and OPeNDAP (subsetting), analysis within cloud without downloading data
- Zarr, using netCDF4-to-Zarr converting services 
  - AWS (computing), Earthdata Cloud (accessing dataset), and Harmony API (conversion/subsetting), analysis within cloud without downloading data
- Zarr, data native to this format
  -  AWS (computing), AWS Open Registry (accessing dataset), and OPeNDAP (subsetting), analysis within cloud without downloading data

...for several cloud analysis scenarios at different scales, including:
- Global SST time series from June 2002 – January 2020
- Global SST spatial plot averaged from June 2002 – January 2020
- Regional SST Anomaly time series – Hawaiian Coral Reef from August 2019 –
January 2020
- Regional SST Anomaly spatial plot – Hawaiian Coral Reef averaged from August
2019 – January 2020
- Application of climatology to derive anomalies for Nino 3.4 box from January 2015 –
March 2016 (2015–2016 El Nino)


## Notes
- Currently no L3/L4 subsetters in Harmony, so must use OPeNDAP for cloud data subsetting
- The Earthdata Search scenario under netCDF4 is not currently possible because MUR 1-km granules are global, they would have to be manually subset post download, this may be tested anyways but it is low priority
