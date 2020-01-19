# The Effects of LSST Cadence Properties on SN Machine Learning Classifications


## Cadence Simulations:

This project consideres the following simulations which are available for download from [zenodo.org](zenodo.org).

| Cadence           | Data DOI                               |
| ----------------- | -------------------------------------- |
| Alt sched         | https://doi.org/10.5281/zenodo.3604380 |
| Alt sched rolling | https://doi.org/10.5281/zenodo.3606957 |
| Kraken 2026       | https://doi.org/10.5281/zenodo.3608294 |
| Kraken 2044       | https://doi.org/10.5281/zenodo.3608326 |
| Nexus 2097        | https://doi.org/10.5281/zenodo.3609116 |
| Rolling 10yr      | https://doi.org/10.5281/zenodo.3609185 |
| Rolling 10yr mix  | https://doi.org/10.5281/zenodo.3609224 |


## Installation and Setup

#### Step 1: Install Dependancies

Python dependencies can be installed for this project using the included `environment.yml` file. To download this repository and setup the environment, run:

```bash
# Download the files from this repo and enter the new directory
git clone https://github.com/LSSTDESC/ML-Cadence
cd ML-Cadence

# create the project environment
conda env create --name ml-cadence --file environment.yml
```



#### Step 2: Download Simulated Light-Curves

The simulated light-curves can be manually downloaded from the links above, or they can be downloaded automatically using `wget` and the `file_list.txt` from this repository. Please note that this will take up a few hundred Gb of storage. To avoid future headaches, please choose the desired output directory with care.

```bash
wget -i file_list.txt -P /desired/output/directory/
```



The downloaded files will be compressed as nested `.tar.gz` files. You can decompress them using the `tar` command:

```bash
tar --to-command='tar -xzvf -' -xzvf file_to_decompress.tar.gz
```



#### Step 3: Specify Data Location in Environment

The path of the downloaded data needs to be specified in the project environment so that the software knows where to find the simulated light-curves. This can be acomplished by replacing `/desired/output/directory/` in the below script:

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
echo 'export BROKER_PROJ_ID="/desired/output/directory/"' >> ./etc/conda/activate.d/env_vars.sh
echo 'unset BROKER_PROJ_ID' >> ./etc/conda/deactivate.d/env_vars.sh

# Finally, don't forget to exit your environment:
conda deactivate
```



Note that for older versions of ``conda`` you may have to use the deprecated command ``source activate`` to activate the environment.