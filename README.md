# The Effects of LSST Cadence Properties on SN Machine Learning Classifications



## Installation and Setup

#### Step 1: Install Dependencies

Python dependencies can be installed for this project using the included `environment.yml` file. To download this repository and setup the environment, run:

```bash
# Download the files from this repo and enter the new directory
git clone https://github.com/LSSTDESC/ML-Cadence
cd ML-Cadence

# create the project environment
conda env create --name ml-cadence --file environment.yml
```

The `ml-cadence` environment can then be entered and exited as necessary using the commands `conda activate ml-cadence` and `conda deactivate` respectively.



#### Step 2: Download Simulated Light-Curves

Please note that the downloaded data will take up a several hundred GB of storage. To avoid future headaches, choose where you will save the downloaded data with care. 



The simulated light-curves can be downloaded automatically using `wget` and the `file_list.txt` file from this repository. For convenience, the  `timeout` and `tries` arguments can be used to indefinitely retry a failed download and the  `continue` flag can be included to avoid restarting a failed download from scratch.

```bash
wget --continue --timeout 0 --tries 0 -i file_list.txt -P /desired/output/directory/
```



The downloaded files will be nested, compressed files using a mix of the `.gz` and `.tar.gz` formats. You can decompress them using the following commands:

```bash
tar -xvzf file_to_decompress.tar.gz --verbose
gunzip file_to_decompress/*/*.gz --verbose
```



#### Step 3: Specify Data Location in Environment

The path of the downloaded data needs to be specified in the project environment so that the software knows where to find the simulated light-curves. If you are using a `conda` environment (as suggested above), this can be accomplished by replacing `/desired/output/directory/` in the below script:

```bash
# Instantiate the new environment
conda activate ml-cadence

# Go to the environment's home directory
cd $CONDA_PREFIX

# Create files to run on startup and exit
mkdir -p ./etc/conda/activate.d
mkdir -p ./etc/conda/deactivate.d
touch ./etc/conda/activate.d/env_vars.sh
touch ./etc/conda/deactivate.d/env_vars.sh

# Add environmental variables
## Change /desired/output/directory/ on the following line ##
echo 'export CADENCE_SIMS="/desired/output/directory/"' >> ./etc/conda/activate.d/env_vars.sh
echo 'unset CADENCE_SIMS' >> ./etc/conda/deactivate.d/env_vars.sh

# Finally, don't forget to exit your environment:
conda deactivate
```



## Cadence Simulations:

This project considers the following simulations which are available for download from [zenodo.org](zenodo.org).

| Cadence           | Data DOI                               |
| ----------------- | -------------------------------------- |
| Alt sched         | https://doi.org/10.5281/zenodo.3604380 |
| Alt sched rolling | https://doi.org/10.5281/zenodo.3606957 |
| Kraken 2026       | https://doi.org/10.5281/zenodo.3608294 |
| Kraken 2044       | https://doi.org/10.5281/zenodo.3608326 |
| Nexus 2097        | https://doi.org/10.5281/zenodo.3609116 |
| Rolling 10yr      | https://doi.org/10.5281/zenodo.3609185 |
| Rolling 10yr mix  | https://doi.org/10.5281/zenodo.3609224 |



#### Data Model

Simulated light-curves are divided into directories based on the model used in the simulation. For certain types of astronomical objects, multiple models were used. Light-curves from different directories/models should not be taken to represent distinct types or subtypes of objects. A summary of the models is as follows:



|Model Number    |  Model Name  |
|:--:|:--:|
|                  11       |  SNIa-normal |
|                    2       |        SNCC-II  |
|                    3       |       SNCC-Ibc  |
|                   2       |        SNCC-II  |
|                   3       |       SNCC-Ibc  |
|                   2       |        SNCC-II  |
|                  41       |      SNIa-91bg  |
|                  43       |         SNIa-x  |
|                  51       |             KN  |
|                  60       |         SLSN-I  |
|                  99       |           PISN  |
|                  99       |           ILOT  |
|                  99       |           CART  |
|                  64       |            TDE  |
|                  70       |            AGN  |
|                  80       |        RRlyrae  |
|                  81       |         Mdwarf  |
|                  83       |            EBE  |
|                  84       |           MIRA  |
|                  99       |   uLens-Binary  |
|                  91        |    uLens-Point  |
|                  99       |   uLens-STRING  |
|                  91        |    uLens-Point  |



Light-curves are saved using the `SNANA` file format where files come in pairs: a header file postfixed with `HEAD.fits` and a photometry file postfixed with `PHOT.fits`. The header file provides meta-data about the observed targets (e.g., `RA` and `Dec`). The photometry file contains the simulated light-curve. Each file containing information for multiple supernovae. Definitions are provided below for a handful of columns in each file type:


| Header File Column | Value Description                                            |
| ------------------ | ------------------------------------------------------------ |
| `SNID`             | Unique object identifier                                     |
| `RA`, `DECL`       | On sky coordinates of the simulated objects                  |
| `MWEBV`            | Simulated Milky Way extinction                              |
| `PTROBS_MIN`       | The row number (index - 1) in the corresponding photometry table where data for the given object starts |
| `PTROBS_MAX`       | The row number (index - 1) in the corresponding photometry table where data for the given object starts |
| `SIM_MODEL_NAME`   | Name of the model used to simulate the light-curve           |

| Photometry File Column | Value Description       |
| ---------------------- | ----------------------- |
| `MJD`                  | Date of the observation |
| `FLT`                  | The observed filter     |
| `FIELD`                | The field of the observation |
| `PHOTFLAG`     | Either `0` (non-detection), `4096` (detection), or `6144` (first trigger) |
| `PHOTPROB`               |                         |
| `FLUXCAL`                |                         |
| `FLUXCALERR`             |                         |
| `PSF_SIG1`               |                         |
| `ZEROPT`                | The photometric zero point (`27.5`) |
| `SIM_MAGOBS`                | The simulated magnitude of the observations |
