#!/usr/bin/env python3.7
# -*- coding: UTF-8 -*-

"""Read and parse simulated light-curves for different cadences

Data is both parsed and represented by the ``CadenceData`` object which
is compatible with the ``snmachine`` package.
"""

import multiprocessing as mp
from glob import glob
from os import environ, path

import numpy as np
from astropy.io import fits
from astropy.table import Table
from numpy.lib import recfunctions as rfn

# To manage sharing of information across processes
MANAGER = mp.Manager()


def read_photometry_file(header_path):
    """Read simulated light-curves from file

    Files are expected in pairs of a header file (`*HEAD.fits`) with target
    meta data and a photometry file (`*PHOT.fits`) with simulated light-curves.

    Args:
        header_path (str): Path of the header file

    Returns:
        - An array of data from the header file
        - An array of data from the photometry file
    """

    # Map of column names to names that snmachine/sncosmo will recognize
    column_name_mapping = {
        'MJD': 'mjd',
        'FLT': 'filter',
        'FIELD': 'field',
        'PHOTFLAG': 'photflag',
        'PHOTPROB': 'photprob',
        'FLUXCAL': 'flux',
        'FLUXCALERR': 'flux_error',
        'PSF_SIG1': 'psf_sig1',
        'SKY_SIG': 'sky_sig',
        'ZEROPT': 'zp',
        'SIM_MAGOBS': 'sim_magobs'
    }

    # Data types to use when reading in the photometry file
    dtypes = [
        ('MJD', '>f8'), ('FLT', 'U10'), ('FIELD', '|S12'),
        ('PHOTFLAG', '>i4'), ('PHOTPROB', '>f4'),
        ('FLUXCAL', '>f4'), ('FLUXCALERR', '>f4'),
        ('PSF_SIG1', '>f4'), ('SKY_SIG', '>f4'),
        ('ZEROPT', '>f4'), ('SIM_MAGOBS', '>f4')
    ]

    with fits.open(header_path) as header_hdulist:
        meta_data = header_hdulist[1].data

    phot_file_path = header_path.replace('HEAD', 'PHOT')
    with fits.open(phot_file_path) as photometry_hdulist:
        # Typecasting to an array avoids astropy bugs/performance issues
        phot_data = np.array(photometry_hdulist[1].data, dtype=dtypes)

        # Rename columns to sncosmo friendly format
        phot_data = rfn.rename_fields(phot_data, column_name_mapping)

        # Rename filters to sncosmo friendly format
        lowercase = np.char.strip(np.char.lower(phot_data['filter']))
        phot_data['filter'] = np.char.add('lsst', lowercase)

    return meta_data, phot_data


class CadenceData:
    def __init__(self, cadence, parent_dir=None):
        """Represents simulated light-curves from a given LSST cadence

        Args:
            cadence    (str): The name of the simulated cadence to load
            parent_dir (str): The parent directory of simulated light-curves
        """

        try:
            parent_dir = parent_dir if parent_dir else environ['CADENCE_SIMS']

        except KeyError:
            raise FileNotFoundError(
                'You must either specify `CADENCE_SIMS` in the current '
                'environment or pass the `parent_dir` argument to this class'
            )

        # Todo: allow selection of a subset of models
        fits_files = glob(path.join(parent_dir, f'{cadence}/**/*HEAD.FITS'))

        # Todo: add multiprocessing for file parsing
        # self.data_dict = MANAGER.dict()
        # with mp.Pool() as pool:
        #     map = pool.imap(self._add_data_to_dict, fits_files)
        #     tuple(tqdm(map, total=len(fits_files)))  # Execute imap

        # Attributes expected by snmachine
        self.data = dict()  # {object id: Table}
        self.filter_set = ['lsst' + b for b in 'ugrizy']

        for fpath in fits_files:
            self._read_data_from_header_file(fpath)

    def _read_data_from_header_file(self, header_path):
        """Add light-curves from a single fits file to the class dictionary

        Args:
            header_path (str): The path of the `*HEAD.fits`
        """

        meta_data, phot_data = read_photometry_file(header_path)
        model = int(header_path.split('MODEL')[-1].split('/')[0])
        for record in meta_data:
            # Format data as an astropy table
            data_start_idx = record['PTROBS_MIN'] - 1
            data_end_idx = record['PTROBS_MAX']
            target_data = Table(phot_data[data_start_idx: data_end_idx])
            target_data['zpsys'] = 'AB'

            # Add basic meta data to the table
            snid = record['SNID']
            target_data.meta['snid'] = snid
            target_data.meta['ra'] = record['RA']
            target_data.meta['dec'] = record['DECL']
            target_data.meta['type'] = record[model]
            target_data.meta['z'] = record['SIM_REDSHIFT_CMB']
            self.data[snid] = target_data

    # Expected by snmachine
    def get_lightcurve(self, snid):
        """Returns the light-curve for a given target

        Args:
            snid (str): The unique id of a supernova

        Returns:
            An astropy table that conforms with sncosmo requirements
        """

        return self.data[snid]

    @property  # Expected by snmachine
    def object_names(self):
        """Returns a list of Ids for supernovae in the dataset.

        Returns:
            A list of SNe Ids as strings
        """

        return list(self.data.keys())
