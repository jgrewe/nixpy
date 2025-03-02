#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Copyright © 2014 German Neuroinformatics Node (G-Node)

 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted under the terms of the BSD License. See
 LICENSE file in the root of the Project.

 Author: Jan Grewe <jan.grewe@g-node.org>

"""

import nixio as nix
import numpy as np
from PIL import Image as img

import docutils


def load_image():
    image = img.open('boats.png')
    pix = np.array(image)
    channels = list(image.mode)
    return pix, channels


def draw_rect(img_data, position, extent):
    img_data[position[0]:position[0] + extent[0], position[1], :] = 255
    img_data[position[0]:position[0] + extent[0], position[1] + extent[1], :] = 255
    img_data[position[0], position[1]:position[1] + extent[1], :] = 255
    img_data[position[0] + extent[0], position[1]:position[1] + extent[1], :] = 255


def plot_data(tag):
    data_array = tag.references[0]
    img_data = np.zeros(data_array.shape)
    data_array.read_direct(img_data)
    img_data = np.array(img_data, dtype='uint8')
    # positions and extents are double by default, need to convert to int
    pos = tuple(map(int, tag.position))
    ext = tuple(map(int, tag.extent))
    draw_rect(img_data, pos, ext)
    new_img = img.fromarray(img_data)
    if not docutils.is_running_under_pytest():
        new_img.save("../images/single_roi.png")
        new_img.show()


def main():
    img_data, channels = load_image()
    # create a new file overwriting any existing content
    file_name = 'single_roi.nix'
    f = nix.File.open(file_name, nix.FileMode.Overwrite)

    # create a 'Block' that represents a grouping object. Here, the recording session.
    # it gets a name and a type
    block = f.create_block("block name", "nix.session")

    # create a 'DataArray' to take the sinewave, add some information about the signal
    data = block.create_data_array("boats", "nix.image.rgb", data=img_data)
    # add descriptors for width, height and channels
    data.append_sampled_dimension(1, label="height")
    data.append_sampled_dimension(1, label="width")
    data.append_set_dimension(labels=channels)

    # create a Tag, position and extent must be 3-D since the data is 3-D
    position = [170, 50, 0]
    extent = [240, 175, 3]
    tag = block.create_tag('Sailing boat', 'nix.roi', position)
    tag.extent = extent
    tag.references.append(data)

    # let's plot the data from the stored information
    plot_data(tag)
    f.close()


if __name__ == '__main__':
    main()
