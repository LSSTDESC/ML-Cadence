#!/usr/bin/env python3.7
# -*- coding: UTF-8 -*-

"""Read and parse simulated light-curves for different cadences"""

import multiprocessing as mp
from glob import glob
from os import environ, path

from astropy.io import fits
from astropy.table import Table

# To manage sharing of information across processes
MANAGER = mp.Manager()


def get_model_from_path(file_path):
    return int(file_path.split('MODEL')[-1].split('/')[0])


class CadenceData:
    def __init__(self, cadence, parent_dir=None):
        """Represents data from a simulated LSST cadence

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

        # Todo allow selection of a subset of models
        fits_files = glob(path.join(parent_dir, f'{cadence}/**/*HEAD.FITS'))

        # self.data_dict = MANAGER.dict()
        # with mp.Pool() as pool:
        #     map = pool.imap(self._add_data_to_dict, fits_files)
        #     tuple(tqdm(map, total=len(fits_files)))  # Execute imap

        self.data_dict = dict()
        for fpath in fits_files:
            self._add_data_to_dict(fpath)

    def _add_data_to_dict(self, header_path):
        """Add light-curves from a single fits file to the class dictionary

        Args:
            header_path (str): The path of the `*HEAD.fits`
        """

        with fits.open(header_path) as header_hdulist:
            print(header_path)
            meta_data = header_hdulist[1].data

        phot_file_path = header_path.replace('HEAD', 'PHOT')
        with fits.open(phot_file_path) as photometry_hdulist:
            phot_data = photometry_hdulist[1].data

        for record in meta_data:
            target_data = Table(
                phot_data[record['PTROBS_MIN'] - 1: record['PTROBS_MAX']]
            )

            snid = record['SNID']
            target_data.meta['snid'] = snid
            target_data.meta['ra'] = record['RA']
            target_data.meta['dec'] = record['DECL']
            target_data.meta['type'] = record[model]
            target_data.meta['z'] = record['SIM_REDSHIFT_CMB']
            self.data_dict[snid] = target_data

    def get_lightcurve(self, snid):
        """Returns the light-curve for a given target

        Args:
            snid (str): The unique id of a supernova

        Returns:
            An astropy table that conforms with sncosmo requirements
        """

        return self.data_dict[snid]

    def get_object_names(self):
        """Returns a list of Ids for supernovae in the dataset.

        Returns:
            A list of SNe Ids as strings
        """

        return list(self.data_dict.keys())
