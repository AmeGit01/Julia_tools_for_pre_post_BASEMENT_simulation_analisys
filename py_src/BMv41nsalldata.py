#!/usr/bin/env python

import h5py
import csv
import glob
import os
import numpy as np


def get_attribute_t(data_set, attribute):
    """Restituisce un attributo di un dataset HDF5."""
    if isinstance(data_set, h5py.Dataset):
        if attribute in data_set.attrs:
            return data_set.attrs[attribute]
        else:
            print(
                f"ERROR: Dataset '{data_set.name}' "
                f"does not have attribute '{attribute}'"
            )
    return None


# ---------------------------------------------------------
# Set up the output header
# ---------------------------------------------------------

result_header = [
    'Mean wse [m]',
    'Discharge [m3/s]',
    'Wetted area [m2]',
    'Mean bottom elevation [m]',
    'Reference elevation [m]',
    'Wetted geometric length [m]',
    'Total water volume stored in cells [m3]',
    'Total cells conveyance [m3/s]',
    'Total morphological flux (no porosity) [m3/s]',
    'Total bedload transport capacity (no porosity) [m3/s]',
    'Bedl. transp. cap. fraction 1 (no por.)  [m3/s]',
    'Bedl. transp. cap. fraction 2 (no por.)  [m3/s]',
    'Bedl. transp. cap. fraction 3 (no por.)  [m3/s]',
    'Bedl. transp. cap. fraction 4 (no por.)  [m3/s]',
    'Bedl. transp. cap. fraction 5 (no por.)  [m3/s]',
    'Bedl. transp. cap. fraction 6 (no por.)  [m3/s]',
    'Bedl. transp. cap. fraction 7 (no por.)  [m3/s]',
    'Bedl. transp. cap. fraction 8 (no por.)  [m3/s]',
    'Bedl. transp. cap. fraction 9 (no por.)  [m3/s]',
    'Bedl. transp. cap. fraction 10 (no por.)  [m3/s]',
    'Bedl. flux fraction 1 (no por.)  [m3/s]',
    'Bedl. flux fraction 2 (no por.)  [m3/s]',
    'Bedl. flux fraction 3 (no por.)  [m3/s]',
    'Bedl. flux fraction 4 (no por.)  [m3/s]',
    'Bedl. flux fraction 5 (no por.)  [m3/s]',
    'Bedl. flux fraction 6 (no por.)  [m3/s]',
    'Bedl. flux fraction 7 (no por.)  [m3/s]',
    'Bedl. flux fraction 8 (no por.)  [m3/s]',
    'Bedl. flux fraction 9 (no por.)  [m3/s]',
    'Bedl. flux fraction 10 (no por.)  [m3/s]'
]


# ----------------------------------------------------------------
# Nodestrings for which the data have to be saved
# ----------------------------------------------------------------

nodestring_names_saved = [
    'idormetro_Ponte_Cervia',
    'idrometro_Ponte_Zaccon',
    'idrometro_Borgo'
]


# ----------------------------------------------------------------
# Find all files ending with results.h5
# ----------------------------------------------------------------

fileh5 = glob.glob('inputs/*results.h5')

print(f"Found {len(fileh5)} input files:")
print(fileh5)


# ----------------------------------------------------------------
# Create output directory if it does not exist
# ----------------------------------------------------------------

os.makedirs('outputs', exist_ok=True)


# ----------------------------------------------------------------
# Loop over all input files
# ----------------------------------------------------------------

for input_file in fileh5:

    print("\n" + "=" * 60)
    print(f"Processing: {input_file}")
    print("=" * 60)

    with h5py.File(input_file, 'r') as f:

        # ---------------------------------------------------------
        # Get the number of outputs located in StateVar
        # ---------------------------------------------------------

        StateVar = f['/RESULTS/NodeStrg/StateVar/']
        time_step_data = list(StateVar.keys())
        n_time_steps = len(time_step_data)

        # ---------------------------------------------------------
        # Find the number of nodestrings and their names
        # ---------------------------------------------------------

        nodestring_names = f['/NodeStrg/StrNames'][:]

        nodestring_names = [
            name.decode('utf-8') if isinstance(name, bytes) else str(name)
            for name in nodestring_names
        ]

        print(f"Found {len(nodestring_names)} nodestrings:")
        print(nodestring_names)

        # ---------------------------------------------------------
        # Check which requested nodestrings actually exist
        # ---------------------------------------------------------

        nodestring_names_available = [
            name for name in nodestring_names_saved
            if name in nodestring_names
        ]

        nodestring_names_missing = [
            name for name in nodestring_names_saved
            if name not in nodestring_names
        ]

        if nodestring_names_missing:
            print("\nWARNING: The following requested nodestrings "
                  "were not found in the HDF5 file:")

            for name in nodestring_names_missing:
                print(f"  - {name}")

        if not nodestring_names_available:
            print("\nWARNING: None of the requested nodestrings "
                  "was found. Skipping this file.")
            continue

        print(
            f"\nUsing {len(nodestring_names_available)} "
            "nodestrings for output:"
        )
        print(nodestring_names_available)

        # ---------------------------------------------------------
        # Find the indices of the requested nodestrings
        # ---------------------------------------------------------

        nodestring_indices = {
            name: nodestring_names.index(name)
            for name in nodestring_names_available
        }

        # ---------------------------------------------------------
        # List available output times
        # ---------------------------------------------------------

        time_steps = [
            get_attribute_t(StateVar[dat], 't')
            for dat in time_step_data
        ]

        print("\nAvailable output time steps [s]:")
        print(time_steps)

        # ---------------------------------------------------------
        # Initialize output arrays ONLY for requested nodestrings
        # ---------------------------------------------------------

        nodestring_data = {
            name: []
            for name in nodestring_names_available
        }

        # ---------------------------------------------------------
        # Loop over output timesteps
        # ---------------------------------------------------------

        for x, dat in enumerate(time_step_data):

            timestep_array = np.asarray(StateVar[dat][:])

            # Check that the dataset contains all nodestrings
            if timestep_array.shape[0] != len(nodestring_names):
                raise ValueError(
                    f"Unexpected number of nodestrings in dataset "
                    f"'{StateVar[dat].name}': "
                    f"found {timestep_array.shape[0]}, "
                    f"expected {len(nodestring_names)}."
                )

            # Extract data ONLY for the requested nodestrings
            for nodestring_name in nodestring_names_available:

                jj = nodestring_indices[nodestring_name]

                row = np.asarray(timestep_array[jj, :]).reshape(-1)

                # Check that the number of variables matches the header
                if len(row) != len(result_header):
                    raise ValueError(
                        f"Unexpected number of variables for "
                        f"nodestring '{nodestring_name}' "
                        f"at timestep {dat}: "
                        f"found {len(row)}, "
                        f"expected {len(result_header)}."
                    )

                nodestring_data[nodestring_name].append(row.tolist())

        # ---------------------------------------------------------
        # Construct output filename and write CSV files
        # ---------------------------------------------------------

        input_basename = os.path.basename(input_file)

        # Remove "_results.h5"
        nomefile = input_basename.removesuffix('_results.h5')

        for nodestring_name in nodestring_names_available:

            output_file = os.path.join(
                'outputs',
                f'{nomefile}_{nodestring_name}.csv'
            )

            with open(output_file, 'w', newline='', encoding='utf-8') as myFile:

                writer = csv.writer(myFile)

                writer.writerow(result_header)
                writer.writerows(nodestring_data[nodestring_name])

            print(f"Writing {output_file} complete")

print("\nAll files processed.")