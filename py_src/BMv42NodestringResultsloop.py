#!/usr/bin/env python

import h5py
import csv
import glob
import sys
import numpy as np

from collections import defaultdict


def get_attribute_t(data_set, attribute):

    """
    Safely retrieves an attribute from an HDF5 dataset.

    Returns None if the attribute does not exist.
    """

    if not isinstance(data_set, h5py.Dataset):

        print("ERROR: Provided object is not an h5py.Dataset.")

        return None

    if attribute in data_set.attrs:

        return data_set.attrs[attribute]

    else:

        print(
            f"ERROR: Dataset '{data_set.name}' "
            f"does not have attribute '{attribute}'"
        )

        return None


# this find the path of any file with this ending

fileh5 = glob.glob('inputs/*results.h5')

if not fileh5:

    raise FileNotFoundError(
        "No file found matching '*results.h5'"
    )


# Check for nodestring state variables (currently HydState and MorState)

stateVariables = ['HydState', 'MorState']


# =========================================================
# LOOP OVER ALL H5 FILES
# =========================================================

for input_file in fileh5:

    print("\n" + "=" * 70)
    print(f"Processing file: {input_file}")
    print("=" * 70)


    # -----------------------------------------------------
    # Get input filename without path
    # -----------------------------------------------------

    input_basename = input_file.split('/')[-1]


    # Remove "_results.h5"
    nomefile = input_basename.removesuffix('_results.h5')


    # -----------------------------------------------------
    # Reset variables for each input file
    # -----------------------------------------------------

    nodestring_names = []
    Nodestrg_states = {}


    # Get the number of outputs

    with h5py.File(input_file, 'r') as f:


        # find the number of stringdef in the domain and their names

        nodestring_names = f['/NodeStrg/StrNames']

        nodestring_names = [
            nodestring_name.decode('utf-8')
            if isinstance(nodestring_name, bytes)
            else nodestring_name
            for nodestring_name in nodestring_names
            if isinstance(nodestring_name, (str, bytes))
        ]

        n_nodestrings = len(nodestring_names)

        print(f"Found {n_nodestrings} nodestrings:")
        print(nodestring_names)


        for var in stateVariables:

            path = f'/RESULTS/NodeStrg/{var}/'


            # check if var exists

            if path in f:

                stateVar = f[path]

                n_time_steps = len(stateVar)


                # The list of available outputs

                time_step_data = list(stateVar)

                time_steps = [
                    get_attribute_t(
                        stateVar.get(dat),
                        't'
                    )
                    for dat in time_step_data
                ]


                # Get dimension of output

                n_data_columns = (
                    f[path]
                    .get(time_step_data[0])
                    .shape[1]
                )


                # initialize the array for final output 1


