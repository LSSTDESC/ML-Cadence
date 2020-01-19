#!/usr/bin/env python3.7
# -*- coding: UTF-8 -*-

"""Uses ``snmachine`` to extract features from SN light-curves.

Extracted features are cached to file in ecsv format. Cached files are
prefixed with the string  ``{survey name}_{feature method}_{kwarg hash}``
where the last value represents the hash of the keyword arguments. Actual
keyword arguments are included as metadata in the cached file.

Usage Example
-------------

>>> from pathlib import Path
>>>
>>> from snmachine import example_data, snclassifier, snfeatures
>>> from snmachine.sndata import Dataset
>>>
>>> from sample_features import extract_features
>>>
>>> data_dir = Path(example_data) / 'SPCC_SUBSET'
>>> snm_data = Dataset(str(data_dir) + '/')
>>>
>>> waveFeats = snfeatures.WaveletFeatures()
>>> wave_features = extract_features(waveFeats, snm_data, './cache', nprocesses=4)
>>> wave_features
"""

import warnings
from pathlib import Path

import numpy as np
from astropy.table import Table
from snmachine.sndata import Dataset


def _create_cache_dirs(parent):
    """Create directories for caching returns from snmachine

    Args:
        parent (str, Path): Path of the directory to create subdirectories in

    Returns:
        - Path object for directory of cached features
        - Path object for directory of cached classifications
    """

    parent = Path(parent)

    # For extracted features
    features_dir = parent / 'features'

    # For classification probabilities and ROC curves
    class_dir = parent / 'classifications'

    # Any intermediate files (such as multinest chains or GP fits)
    # out_int = parent / 'int'

    cache_dirs = (features_dir, class_dir)
    for directory in cache_dirs:
        directory.mkdir(exist_ok=True, parents=True)

    return cache_dirs


def get_cache_prefix(data, method, **kwargs):
    """Determine the file name prefix for a cached file

    Args:
        data (Dataset): Directory of dataset to extract features for
        method (str): The method used to identify features
        All method specific kwargs used when calling ``extract_features``

    Returns:
         The file prefix as a sting
    """

    ignore_kwargs = (
        'save_chains',
        'chain_directory',
        'nprocesses',
        'save_output',
        'convert_to_binary',
        'output_root'
    )

    kept_kwargs = {k: v for k, v in kwargs.items() if k not in ignore_kwargs}
    return f'{data.survey_name}_{method}_{hash(str(kept_kwargs))}'


# noinspection PyTypeChecker,PyTypeChecker,PyTypeChecker
def extract_features(
        feature_class, data, cache_dir=None, file_prefix=None, **kwargs):
    """Extract features from a dataset and cache the results to a directory

    This function wraps ``feature_class.extract_features`` and caches the
    results to file for faster loading. The builtin functionality of the
    feature sampler to save intermediate files is disabled by default, but
    is still accessible by the key word arguments.

    Args:
        feature_class (Features): Class of the feature extraction technique
        data           (Dataset): Directory of dataset to extract features for
        cache_dir    (str, Path): Optional directory where results are cached
        file_prefix        (str): Optional prefix for the cached files
        Any other kwargs for ``feature_class.extract_features``

    Returns:
        Extracted features as an astropy Table
    """

    # Disable default behavior by parametric sampler to save chain results
    method = type(feature_class).__name__
    if method != 'ParametricFeatures':
        kwargs.setdefault('save_output', False)

    if not cache_dir:
        with warnings.catch_warnings():
            features = feature_class.extract_features(data, **kwargs)

        return features

    # Define paths of cached results
    file_prefix = file_prefix if file_prefix else \
        get_cache_prefix(data, method, **kwargs)

    features_dir, _ = _create_cache_dirs(cache_dir)
    features_path = features_dir / f'{file_prefix}_features.ecsv'
    eigenval_path = features_dir / f'{file_prefix}_eigenvals.ecsv'
    eigenvec_path = features_dir / f'{file_prefix}_eigenvectors.ecsv'
    mean_path = features_dir / f'{file_prefix}_mean.ecsv'

    # Return existing results from file if available
    if features_path.exists():
        features = Table.read(features_path, format='ascii.ecsv')

        # Wavelet features have supplementary data
        if method == 'WaveletFeatures':
            feature_class.PCA_eigenvals = np.loadtxt(eigenval_path)
            feature_class.PCA_eigenvectors = np.loadtxt(eigenvec_path)
            feature_class.PCA_mean = np.loadtxt(mean_path)

    else:
        # If features not cached, calculate them and write them to file
        with warnings.catch_warnings():
            features = feature_class.extract_features(data, **kwargs)

        features.meta.update(kwargs)
        features.write(str(features_path), format='ascii.ecsv')
        if method == 'WaveletFeatures':
            np.savetxt(eigenval_path, feature_class.PCA_eigenvals)
            np.savetxt(eigenvec_path, feature_class.PCA_eigenvectors)
            np.savetxt(mean_path, feature_class.PCA_mean)

    return features
