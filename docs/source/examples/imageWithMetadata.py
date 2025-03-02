#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Copyright © 2014 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

"""
import numpy as np
import nixio as nix
import matplotlib.pyplot as plt

import docutils

from PIL import Image as img


def print_metadata_table(section, ax):
    columns = ['Name', 'Value']
    cell_text = []
    for p in section.items():
        for i, v in enumerate(p[1].values):
            value = str(v)
            if len(value) > 30:
                value = value[:30] + '...'
            if i == 0:
                row_data = [p[0], value]
            else:
                row_data = [p[0], value]

            cell_text.append(row_data)
    if len(cell_text) > 0:
        nrows, ncols = len(cell_text)+1, len(columns)
        ax.axis('off')
        the_table = ax.table(cellText=cell_text,
                               colLabels=columns,
                               loc='center')
        for cell in the_table.get_children():
            cell.set_height(.075)
            cell.set_fontsize(16)


def load_image():
    image = img.open('boats.png')
    pix = np.array(image)
    channels = list(image.mode)
    return pix, channels


def plot_data(data_array):
    img_data = np.zeros(data_array.shape)
    data_array.read_direct(img_data)
    img_data = np.array(img_data, dtype='uint8')
    new_img = img.fromarray(img_data)

    fig = plt.figure()
    img_axis = fig.add_subplot(121)
    img_axis.imshow(new_img)

    info_axis = fig.add_subplot(122)
    print_metadata_table(data_array.metadata, info_axis)
    fig.subplots_adjust(left=0.075, right=0.975, bottom=0.075, top=0.975)
    if docutils.is_running_under_pytest():
        plt.close()
    else:
        fig.savefig('../images/image_with_metadata.png')
        fig.show()


def add_image_information(nix_file):
    section = nix_file.create_section('Image metadata', 'image_source')
    section['Original name'] = 'Boats'
    section['Location'] = 'Port Louis'
    section['Year'] = 2014
    section['Month'] = 'August'
    section['Author'] = 'Self'
    return section


if __name__ == '__main__':
    img_data, channels = load_image()
    # create a new file overwriting any existing content
    file_name = 'image_with_source_example.h5'
    file = nix.File.open(file_name, nix.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type 
    block = file.create_block("block name", "nix.session")

    # create a 'DataArray' to take the sinewave, add some information about the signal
    data = block.create_data_array("lenna", "nix.image.rgb", data=img_data)
    # add descriptors for width, height and channels
    height_dim = data.append_sampled_dimension(1)
    height_dim.label = "height"
    width_dim = data.append_sampled_dimension(1)
    width_dim.label = "width"
    color_dim = data.append_set_dimension()
    color_dim.labels = channels
    section = add_image_information(file)
    data.metadata = section
    # let's plot the data from the stored information
    plot_data(data)
    file.close()
