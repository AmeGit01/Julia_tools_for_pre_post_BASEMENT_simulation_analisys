#!/usr/bin/env python
import h5py
import csv
import glob
import sys
import numpy as np

def get_attribute_t(data_set,attribute):
    if isinstance(data_set, h5py.Dataset):
        if attribute in data_set.attrs:
            return data_set.attrs[attribute]
        else:
            print(f"ERROR: Dataset '{StateVar.get(data_set[0]).name}' does not have attribute '{attribute}'")

#this find the path of any file with this ending
fileh5 = glob.glob('inputs/*results.h5')

#import h5py.File with the *_results.h5 ending
f = h5py.File(fileh5[0],'r')

#Get the number of outputs located in StateVar/ file
StateVar = f['/RESULTS/NodeStrg/StateVar/']
n_time_steps=len(StateVar)

#find the number of stringdef in the domain and their names
nodestring_names = f['/NodeStrg/StrNames']
nodestring_names = [nodestring_name.decode('utf-8') if isinstance(nodestring_name, bytes) else nodestring_name for nodestring_name in nodestring_names if isinstance(nodestring_name, (str, bytes))]

n_nodestrings = len(nodestring_names)
print(f"Found {n_nodestrings} nodestrings:")
print(nodestring_names)

#The list of available outputs
time_step_data=list(StateVar)
time_steps = [get_attribute_t(StateVar.get(dat),'t') for dat in time_step_data]
print("\nAvailable output time steps [s]:")
print(time_steps)

rowname=zip(time_step_data)

#initialize the array for final output 1
all_nodestring_data = np.empty(shape=(0,30+2))
nodestring_data = {}
for nodestring_name in nodestring_names:
    nodestring_data[nodestring_name] = np.empty(shape=(0,30))
#initialize the array for discharge output
discharge = np.empty(shape=(0,n_nodestrings+1))

#loop to gather the outputs
for x in range(0, n_time_steps):
    #for the discharge at each stringdef
    column0 = [i[1] for i in StateVar.get(time_step_data[x])]
    column0.insert(0,time_steps[x])
    discharge = np.append(discharge, [column0], axis=0)
    #the timesteps
    #all the outputs of the stringdef
    tmp = np.append([[time_steps[x], nodestring_names[i]] for i in range(len(nodestring_names))], StateVar.get(time_step_data[x])[:], axis=1)
    all_nodestring_data = np.append(all_nodestring_data, tmp, axis=0)
    for jj,nodestring_name in enumerate(nodestring_names):
        nodestring_data[nodestring_name] = np.append(nodestring_data[nodestring_name], StateVar.get(time_step_data[x])[jj,:].reshape(30, -1).T, axis=0)

#write the csv documents
result_header = ['Mean wse [m]', 'Discharge [m3/s]', 'Wetted area [m2]', 'Mean bottom elevation [m]','Reference elevation [m]',\
                     'Wetted geometric length [m]', 'Total water volume stored in cells [m3]', 'Total cells conveyance [m3/s]',\
                     'Total morphological flux (no porosity) [m3/s]','Total bedload transport capacity (no porosity) [m3/s]', \
                     'Bedl. transp. cap. fraction 1 (no por.)  [m3/s]','Bedl. transp. cap. fraction 2 (no por.)  [m3/s]',\
                     'Bedl. transp. cap. fraction 3 (no por.)  [m3/s]','Bedl. transp. cap. fraction 4 (no por.)  [m3/s]',\
                     'Bedl. transp. cap. fraction 5 (no por.)  [m3/s]','Bedl. transp. cap. fraction 6 (no por.)  [m3/s]',\
                     'Bedl. transp. cap. fraction 7 (no por.)  [m3/s]','Bedl. transp. cap. fraction 8 (no por.)  [m3/s]',\
                     'Bedl. transp. cap. fraction 9 (no por.)  [m3/s]','Bedl. transp. cap. fraction 10 (no por.)  [m3/s]',\
                     'Bedl. flux fraction 1 (no por.)  [m3/s]','Bedl. flux fraction 2 (no por.)  [m3/s]',\
                     'Bedl. flux fraction 3 (no por.)  [m3/s]','Bedl. flux fraction 4 (no por.)  [m3/s]',\
                     'Bedl. flux fraction 5 (no por.)  [m3/s]','Bedl. flux fraction 6 (no por.)  [m3/s]',\
                     'Bedl. flux fraction 7 (no por.)  [m3/s]','Bedl. flux fraction 8 (no por.)  [m3/s]',\
                     'Bedl. flux fraction 9 (no por.)  [m3/s]','Bedl. flux fraction 10 (no por.)  [m3/s]'
        ]

# #csv with all the available output, witout specification on the output time and the stringdef name (to be added in a further development)
# myFile = open('outputs/results.csv', 'w')
# header = ['t [s]','Nodestring name [-]']
# header.extend(result_header)
# with myFile:
#     writer = csv.writer(myFile)
#     writer.writerow(result_header)
#     writer.writerows(all_nodestring_data)
# print("\nWriting results.csv complete")
# 
# for nodestring_name in nodestring_names:
#     myFile = open(f'outputs/results_{nodestring_name}.csv', 'w')
#     with myFile:
#         writer = csv.writer(myFile)
#         writer.writerow(result_header)
#         writer.writerows(nodestring_data[nodestring_name])
#     print(f"Writing results_{nodestring_name}.csv complete")

#csv with discharge result only, each column represents one stringdef and the rows are the output timesteps (not precised yet, done in a further developent)
my2File = open('outputs/discharge.csv', 'w')
header = ['t [s]']
header.extend([f'Q_{name} [m3/s]' for name in nodestring_names])
with my2File:
    writer = csv.writer(my2File)
    writer.writerow(header)
    writer.writerows(discharge)
print("Writing Discharge.csv complete")