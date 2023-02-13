import numpy as np
import matplotlib.pyplot as plt
import os

# data_file_name = f"data_array_"
files = []
for file in os.listdir(os. getcwd()):
    if file.startswith("data_array_"):
        files.append(file)
        print(files)

for i, filename in enumerate(files):
    print(f"{(i+1)} : {filename}")

data_number = int(input("Please choose which data to print."))
data_file = files[data_number-1]


arrayim = np.loadtxt(data_file, delimiter=',')
# print(arrayim)
fig = plt.figure(figsize=(6, 3.2))
ax = fig.add_subplot(111)
ax.set_title('colorMap')
plt.imshow(arrayim)
ax.set_aspect('equal')

cax = fig.add_axes([0.12, 0.1, 0.78, 0.8])
cax.get_xaxis().set_visible(False)
cax.get_yaxis().set_visible(False)
cax.patch.set_alpha(0)
cax.set_frame_on(False)
plt.colorbar(orientation='vertical')
plt.show()