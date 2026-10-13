#!/usr/bin/env python

import h5py
import csv
import glob
import os
import numpy as np


def get_attribute_t(data_set, attribute):

    if isinstance(data_set, h5py.Dataset):

        if attribute in data_set.attrs:

            return data_set.attrs[attribute]

        else:

            print(
                f"ERROR: Dataset '{data_set.name}' "
                f"does not have attribute '{attribute}'"
            )


# Find all files ending with results.h5
fileh5 = glob.glob('inputs/*results.h5')

print(f"Found {len(fileh5)} input files:")
print(fileh5)


# Loop over all input files
for input_file in fileh5:

    print("\n" + "=" * 60)
    print(f"Processing: {input_file}")
    print("=" * 60)

    # Open HDF5 file
    f = h5py.File(input_file, 'r')

    # ---------------------------------------------------------
    # Get the number of outputs located in StateVar
    # ---------------------------------------------------------

    StateVar = f['/RESULTS/NodeStrg/StateVar/']
    n_time_steps = len(StateVar)

    # ---------------------------------------------------------
    # Find the number of nodestrings and their names
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # List of available outputs
    # ---------------------------------------------------------

    time_step_data = list(StateVar)

    time_steps = [
        get_attribute_t(StateVar.get(dat), 't')
        for dat in time_step_data
    ]

    print("\nAvailable output time steps [s]:")
    print(time_steps)

    # ---------------------------------------------------------
    # Initialize discharge array
    # ---------------------------------------------------------

    discharge = np.empty(shape=(0, n_nodestrings + 1))

    # ---------------------------------------------------------
    # Loop over output timesteps
    # ---------------------------------------------------------

    for x in range(0, n_time_steps):

        # Discharge at each nodestring
        column0 = [
            i[1] for i in StateVar.get(time_step_data[x])
        ]

        column0.insert(0, time_steps[x])

        discharge = np.append(
            discharge,
            [column0],
            axis=0
        )

    # ---------------------------------------------------------
    # Construct output filename
    #
    # Example:
    # inputs/test_results.h5
    #       ↓
    # outputs/test_discharge.csv
    # ---------------------------------------------------------

    input_basename = os.path.basename(input_file)

    # Remove "_results.h5"
    nomefile = input_basename.removesuffix('_results.h5')

    output_file = os.path.join(
        'outputs',
        f'{nomefile}_discharge.csv'
    )

    # ---------------------------------------------------------
    # Write discharge CSV
    # ---------------------------------------------------------

    header = ['t [s]']

    header.extend(
        [f'Q_{name} [m3/s]' for name in nodestring_names]
    )

    with open(output_file, 'w', newline='') as my2File:

        writer = csv.writer(my2File)

        writer.writerow(header)
        writer.writerows(discharge)

    print(f"Writing {output_file} complete")

    # Close HDF5 file
    f.close()

