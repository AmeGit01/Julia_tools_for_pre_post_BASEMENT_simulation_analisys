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
        print(f"ERROR: Dataset '{data_set.name}' does not have attribute '{attribute}'")
        return None

#this find the path of any file with this ending
fileh5 = glob.glob('*results.h5')
if not fileh5:
    raise FileNotFoundError("No file found matching '*results.h5'")

# Check for nodestring state variables (currently HydState and MorState)
stateVariables = ['HydState','MorState']
nodestring_names = []
Nodestrg_states = {}
#Get the number of outputs
with h5py.File(fileh5[0], 'r') as f:
    #find the number of stringdef in the domain and their names
    nodestring_names = f['/NodeStrg/StrNames']
    nodestring_names = [nodestring_name.decode('utf-8') if isinstance(nodestring_name, bytes) else nodestring_name for nodestring_name in nodestring_names if isinstance(nodestring_name, (str, bytes))]
    n_nodestrings = len(nodestring_names)
    for var in stateVariables:
        path = f'/RESULTS/NodeStrg/{var}/'
        # check if var exists
        if path in f:
            stateVar = f[path]
            n_time_steps=len(stateVar)

            #The list of available outputs
            time_step_data=list(stateVar)
            time_steps = [get_attribute_t(stateVar.get(dat),'t') for dat in time_step_data]

            # Get dimension of output
            n_data_columns = f[path].get(time_step_data[0]).shape[1]

            #initialize the array for final output 1
            all_nodestring_data = np.empty(shape=(0,n_data_columns+2))
            nodestring_data = {}
            for nodestring_name in nodestring_names:
                nodestring_data[nodestring_name] = np.empty(shape=(0,n_data_columns))
            #initialize the array for discharge output
            discharge = np.empty(shape=(0,n_nodestrings+1))

            #loop to gather the outputs
            for x in range(0, n_time_steps):
                column0 = [i[1] for i in stateVar.get(time_step_data[x])]
                column0.insert(0,time_steps[x])
                discharge = np.append(discharge, [column0], axis=0)
                #the timesteps
                #all the outputs of the stringdef
                tmp = np.append([[time_steps[x], nodestring_names[i]] for i in range(len(nodestring_names))], stateVar.get(time_step_data[x])[:], axis=1)
                all_nodestring_data = np.append(all_nodestring_data, tmp, axis=0)
                for jj,nodestring_name in enumerate(nodestring_names):
                    nodestring_data[nodestring_name] = np.append(nodestring_data[nodestring_name], stateVar.get(time_step_data[x])[jj,:].reshape(n_data_columns, -1).T, axis=0)
            Nodestrg_states[var] = [discharge,nodestring_data,all_nodestring_data]

result_headers = {
    'HydState': [
        'Mean wse [m]', 'Discharge [m3/s]', 'Wetted area [m2]', 'Mean bottom elevation [m]',
        'Reference elevation [m]', 'Wetted geometric length [m]',
        'Total water volume stored in cells [m3]'
    ],
    'MorState': [
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
}

# Keep the canonical order HydState -> MorState but only include those present
preferred_order = ['HydState', 'MorState']
present_vars = [v for v in preferred_order if v in Nodestrg_states]

if not present_vars:
    raise RuntimeError("No nodestring state variables found to write.")

# Build combined header
combined_header = ['t [s]', 'Nodestring name [-]']
for v in present_vars:
    combined_header.extend(result_headers[v])

# Gather combined rows keyed by (t, nodestring)
# Each state contributes its own set of columns appended in preferred_order
data_by_key = defaultdict(lambda: {v: None for v in present_vars})

# Fill from each present state
for v in present_vars:
    all_nodestring_data = Nodestrg_states[v][2]  # shape: [Nrows, 2 + n_cols_v]
    # Ensure it's numpy array
    arr = np.asarray(all_nodestring_data)
    # Loop rows and store columns after the first 2 (t, name)
    for row in arr:
        t_val = float(row[0])
        name_val = str(row[1])
        cols = row[2:].tolist()
        data_by_key[(t_val, name_val)][v] = cols

# Convert dict to sorted rows (by time, then name)
def build_row(key):
    t_val, name_val = key
    row = [t_val, name_val]
    for v in present_vars:
        cols = data_by_key[key][v]
        if cols is None:
            # If somehow missing, pad with NaNs
            cols = [np.nan] * len(result_headers[v])
        row.extend(cols)
    return row

sorted_keys = sorted(data_by_key.keys(), key=lambda x: (x[0], x[1]))

# Write results.csv (all nodestrings, all times)
with open('csv_files/results.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(combined_header)
    for key in sorted_keys:
        writer.writerow(build_row(key))
print("Writing results.csv complete")

# Write per-nodestring files
unique_names = sorted({name for (_, name) in sorted_keys})
for nodestring_name in unique_names:
    with open(f'csv_files/results_{nodestring_name}.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        # Header: t + combined state headers
        per_header = ['t [s]']
        for v in present_vars:
            per_header.extend(result_headers[v])
        writer.writerow(per_header)

        # Rows only for this nodestring, sorted by time
        keys_for_name = sorted([k for k in sorted_keys if k[1] == nodestring_name], key=lambda x: x[0])
        for key in keys_for_name:
            t_val, _ = key
            row = [t_val]
            for v in present_vars:
                cols = data_by_key[key][v]
                if cols is None:
                    cols = [np.nan] * len(result_headers[v])
                row.extend(cols)
            writer.writerow(row)
    print(f"Writing results_{nodestring_name}.csv complete")

# Write Discharge.csv only if HydState is present
if 'HydState' in present_vars:
    discharge = Nodestrg_states['HydState'][0]  # shape: [Ntimes, 1 + n_nodestrings], first col is t
    discharge = np.asarray(discharge)
    # header: t + one column per nodestring
    header = ['t [s]'] + [f'Q_{name} [m3/s]' for name in nodestring_names]
    with open('csv_files/Discharge.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        # Ensure numerical rows
        for row in discharge:
            writer.writerow(row.tolist())
    print("Writing Discharge.csv complete")
else:
    print("HydState not present -> skipping Discharge.csv")
