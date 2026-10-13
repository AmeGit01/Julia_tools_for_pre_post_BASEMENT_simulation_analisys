#!/usr/bin/env python
"""Export discharge for every *results.h5 file in inputs/ to outputs/*_discharge.csv."""

import csv
import glob
import os

import h5py


def get_attribute_t(dataset, attribute):
    """Return an HDF5 dataset attribute, or None if it is missing."""
    if isinstance(dataset, h5py.Dataset):
        return dataset.attrs.get(attribute)
    return None


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
        nodestring_names = [
            item.decode("utf-8") if isinstance(item, bytes) else str(item)
            for item in names_raw
        ]

        state_path = "/RESULTS/NodeStrg/HydState"
        if state_path not in f:
            print("HydState not present -> skipping discharge for this file.")
            continue

        state_var = f[state_path]
        timestep_names = sorted(
            state_var.keys(),
            key=lambda key: (int(key) if key.isdigit() else key)
        )
        if not timestep_names:
            print("HydState contains no output timesteps -> skipping.")
            continue

        rows = []
        for timestep_name in timestep_names:
            dataset = state_var[timestep_name]
            time_value = get_attribute_t(dataset, "t")
            if time_value is None:
                print(
                    f"WARNING: '{dataset.name}' has no 't' attribute; "
                    "using the timestep key as the time value."
                )
                time_value = timestep_name

            values = dataset[:]
            if values.ndim != 2 or values.shape[0] != len(nodestring_names):
                raise ValueError(
                    f"Unexpected shape {values.shape} in '{dataset.name}'; "
                    f"expected one row per nodestring ({len(nodestring_names)})."
                )
            if values.shape[1] < 2:
                raise ValueError(
                    f"Dataset '{dataset.name}' has fewer than 2 columns; "
                    "cannot read discharge from column 2."
                )

            rows.append([time_value] + [row[1] for row in values])

        basename = os.path.basename(input_file)
        stem = basename[:-len("_results.h5")] if basename.endswith("_results.h5") else os.path.splitext(basename)[0]
        output_file = os.path.join("outputs", f"{stem}_discharge.csv")
        header = ["t [s]"] + [f"Q_{name} [m3/s]" for name in nodestring_names]

        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(rows)

        print(f"Writing {output_file} complete")

print("\nAll files processed.")
