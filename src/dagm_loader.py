from PIL import Image
import os
import h5py
import re
import numpy as np

def create_dataset(path, dataset_type, image_size=256, pixel_shift=16):
    x_images = os.listdir(path + '/Label/')
    x_images.pop()
    dataframe = h5py.File(dataset_type + "_dataset.hdf5", "w")
    image_shape = (image_size, image_size, 1)

    for image in x_images:
        for y in range(0, 512 - image_size, pixel_shift):
            for x in range(0, 512 - image_size, pixel_shift):
                picture = Image.open(path + re.sub('_label','',image))
                label_path = path + 'Label/' + image
                cut_name = re.sub('.PNG', '', image) + '_' + str(x) + '_'+ str(y) + '.PNG'
                cut_picture = picture.crop((x, y, image_size + x, image_size + y))
                cut_picture = np.asarray(cut_picture)

                data = dataframe.create_dataset(cut_name, shape=image_shape, data=cut_picture)
                picture_label = Image.open(label_path)
                cut_picture_label = picture_label.crop((x, y, image_size + x, image_size + y))

                black_count = [1 for row in np.asarray(cut_picture_label) for column in row if not column == 0]
                if len(black_count) == 0:
                    data.attrs['class_type'] = 0
                else:
                    data.attrs['class_type'] = 1

    dataframe.close()
    
    
def load_dataset(dataset_type, path=None):
    if path:
        dataset_type = os.path.join(path, dataset_type)
    dataset = h5py.File(dataset_type + '_dataset.hdf5', 'r')
    dataset_name = list(dataset)

    y = []
    x = []
    for name in dataset_name:
        data = dataset[name]
        y.append(data.attrs['class_type'])
        x_item = data[:]
        x.append(x_item)

    y = np.array(y)
    y = y.reshape(len(y),1)
    x = np.array(x)
    dataset.close()
    return x, y