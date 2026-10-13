#!/usr/bin/env python
"""Export HydState and MorState data for selected nodestrings from every input results file."""

import csv
import glob
import os

import h5py
import numpy as np


def get_attribute_t(dataset, attribute):
    """Return an HDF5 dataset attribute, or None if it is missing."""
    if isinstance(dataset, h5py.Dataset):
        return dataset.attrs.get(attribute)
    return None


# Edit this list to choose which nodestrings are exported.
nodestring_names_saved = [
    "idormetro_Ponte_Cervia",
    "idrometro_Ponte_Zaccon",
    "idrometro_Borgo",
]

result_headers = {
    "HydState": [
        "Mean wse [m]",
        "Discharge [m3/s]",
        "Wetted area [m2]",
        "Mean bottom elevation [m]",
        "Reference elevation [m]",
        "Wetted geometric length [m]",
        "Total water volume stored in cells [m3]",
    ],
    "MorState": [
        "Total cells conveyance [m3/s]",
        "Total morphological flux (no porosity) [m3/s]",
        "Total bedload transport capacity (no porosity) [m3/s]",
        "Bedl. transp. cap. fraction 1 (no por.) [m3/s]",
        "Bedl. transp. cap. fraction 2 (no por.) [m3/s]",
        "Bedl. transp. cap. fraction 3 (no por.) [m3/s]",
        "Bedl. transp. cap. fraction 4 (no por.) [m3/s]",
        "Bedl. transp. cap. fraction 5 (no por.) [m3/s]",
        "Bedl. transp. cap. fraction 6 (no por.) [m3/s]",
        "Bedl. transp. cap. fraction 7 (no por.) [m3/s]",
        "Bedl. transp. cap. fraction 8 (no por.) [m3/s]",
        "Bedl. transp. cap. fraction 9 (no por.) [m3/s]",
        "Bedl. transp. cap. fraction 10 (no por.) [m3/s]",
        "Bedl. flux fraction 1 (no por.) [m3/s]",
        "Bedl. flux fraction 2 (no por.) [m3/s]",
        "Bedl. flux fraction 3 (no por.) [m3/s]",
        "Bedl. flux fraction 4 (no por.) [m3/s]",
        "Bedl. flux fraction 5 (no por.) [m3/s]",
        "Bedl. flux fraction 6 (no por.) [m3/s]",
        "Bedl. flux fraction 7 (no por.) [m3/s]",
        "Bedl. flux fraction 8 (no por.) [m3/s]",
        "Bedl. flux fraction 9 (no por.) [m3/s]",
        "Bedl. flux fraction 10 (no por.) [m3/s]",
    ],
}
preferred_order = ["HydState", "MorState"]

fileh5 = sorted(glob.glob("inputs/*results.h5"))
if not fileh5:
    raise FileNotFoundError("No file found matching 'inputs/*results.h5'")

os.makedirs("outputs", exist_ok=True)
print(f"Found {len(fileh5)} input files:")
for path in fileh5:
    print(f"  {path}")

for input_file in fileh5:
    print("\n" + "=" * 60)
    print(f"Processing: {input_file}")
    print("=" * 60)

    with h5py.File(input_file, "r") as f:
        names_raw = f["/NodeStrg/StrNames"][:]
        all_names = [
            item.decode("utf-8") if isinstance(item, bytes) else str(item)
            for item in names_raw
        ]

        selected_names = [name for name in nodestring_names_saved if name in all_names]
        missing_names = [name for name in nodestring_names_saved if name not in all_names]
        for name in missing_names:
            print(f"WARNING: requested nodestring '{name}' not found in this file.")

        if not selected_names:
            print("None of the requested nodestrings was found; skipping this file.")
            continue

        present_vars = [
            var for var in preferred_order
            if f"/RESULTS/NodeStrg/{var}" in f
        ]
        if not present_vars:
            print("Neither HydState nor MorState is present; skipping this file.")
            continue

        # Read data by timestep and nodestring. Each state has its own header.
        data_by_name = {name: {} for name in selected_names}

        for var in present_vars:
            state_var = f[f"/RESULTS/NodeStrg/{var}"]
            timestep_names = sorted(
                state_var.keys(),
                key=lambda key: (int(key) if key.isdigit() else key)
            )
            expected_columns = len(result_headers[var])

            for timestep_name in timestep_names:
                dataset = state_var[timestep_name]
                time_value = get_attribute_t(dataset, "t")
                if time_value is None:
                    print(
                        f"WARNING: '{dataset.name}' has no 't' attribute; "
                        "using the timestep key as the time value."
                    )
                    time_value = timestep_name

                values = np.asarray(dataset[:])
                if values.ndim != 2 or values.shape[0] != len(all_names):
                    raise ValueError(
                        f"Unexpected shape {values.shape} in '{dataset.name}'; "
                        f"expected one row per nodestring ({len(all_names)})."
                    )
                if values.shape[1] != expected_columns:
                    raise ValueError(
                        f"Unexpected number of columns in '{dataset.name}': "
                        f"found {values.shape[1]}, expected {expected_columns} "
                        f"for {var}."
                    )

                for name in selected_names:
                    index = all_names.index(name)
                    data_by_name[name].setdefault(time_value, {})[var] = values[index, :].tolist()

        basename = os.path.basename(input_file)
        stem = basename[:-len("_results.h5")] if basename.endswith("_results.h5") else os.path.splitext(basename)[0]

        for name in selected_names:
            header = ["t [s]"]
            for var in present_vars:
                header.extend(result_headers[var])

            output_file = os.path.join("outputs", f"{stem}_{name}.csv")
            rows = []
            for time_value in sorted(data_by_name[name], key=lambda value: float(value)):
                row = [time_value]
                state_data = data_by_name[name][time_value]
                for var in present_vars:
                    values = state_data.get(var)
                    if values is None:
                        values = [np.nan] * len(result_headers[var])
                    row.extend(values)
                rows.append(row)

            with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                writer.writerows(rows)

            print(f"Writing {output_file} complete")

print("\nAll files processed.")
