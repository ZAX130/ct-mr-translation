from preprocessing import *
import os
import numpy as np

"""
    Before running the script, make sure to have the scans in the structure
    below. Names may vary:

    input:
    training scans - ./data/name_of_data/train/*.nii.gz
    test scans - ./data/name_of_data/test/*.nii.gz
    annotation masks - ./data/annotations/*.nii.gz (optional)
    crop_file - *.npz (optional, manual crops of scan of region of interest) 

    output:
    training - ./data/name_of_data/train/trainA
             - ./data/name_of_data/train/trainB
             - ./data/name_of_data/train/annotations
    
    testing  - ./data/name_of_data/train/testA
             - ./data/name_of_data/train/testB
             - ./data/name_of_data/train/annotations

    Then transfer trainA, trainB, testA, testB to CycleGAN/datasets/name_of_data
"""

def get_patches(scan_path, scan_name, crops):
    scan = np.load(scan_path)['data']

    # crop scan using segmentation - currently not in use
    # seg = np.load(seg_path)['data']
    # cropped_scan = crop_volume(scan, seg, is_mr)
    
    if crops.item().get(scan_name) is not None:    
        idx = crops.item().get(scan_name)
        scan = scan[idx[0]:idx[1], idx[2]:idx[3], idx[4]: idx[5]]
    
    # get all patches
    all_patches = get_all_patches(scan, side='c', dim=256, step=(128, 128))
    
    print(all_patches.shape)

    return all_patches


def prepare_data(root_path, crops, is_train = True):

    data_type = 'train'
    if is_train is False:
        data_type = 'test'

    # root_path = './data/visceral_full'
    
    train_path = root_path + '/' + data_type
    dom_a_path = train_path + '/{}A'.format(data_type) # CT
    dom_b_path = train_path + '/{}B'.format(data_type) # MR
    
    # train_seg_path = train_path + '/annotations'
    # seg_root_path = root_path + '/annotations'
    
    nii_ext_name = '.nii.gz'
    scan_paths_train = get_image_paths_given_substr(train_path, '.nii')
    scan_names = [ p.split('/')[-1].strip('.nii.gz') for p in scan_paths_train ]

    # os.makedirs(train_seg_path, exist_ok=True)
    os.makedirs(dom_a_path, exist_ok=True)
    os.makedirs(dom_b_path, exist_ok=True)

    print("Converting zipped nii to npz with crops")
    prepare_volume_as_npz(scan_paths_train, nii_ext_name, train_path, crops)

    # print("Getting all segmentations")
    # prepare_seg_as_npz(seg_root_path, scan_names, train_seg_path)

    # only generate slices when preparing training data!
    if is_train is True:
        
        print("Processing npz volume files to npz image slices")
        
        npz_file_paths = get_image_paths_given_substr(train_path, '.npz')

        for scan_path in npz_file_paths:
            scan_name = scan_path.replace(".npz", "").split('/')[-1]
            # seg_path = train_seg_path + '/' + scan_name + '.npz'
            is_ct = is_ct_file(scan_path)
            is_mr = not is_ct

            # get all patches
            all_patches = get_patches(scan_path, scan_name, crops)

            for i, patch in enumerate(all_patches):
                dom_path = dom_b_path
            
                if (is_ct):
                    dom_path = dom_a_path

                save_path = dom_path + '/' + scan_name + '_' + str(i) + '.npz'
            
                # patch = resize_img(patch, 128)
                np.savez(save_path, data=patch)


if __name__ == '__main__':
    crops = np.load('./visceral_crops.npz', allow_pickle=True)['data']

    # prepare train data here
    prepare_data('./data/visceral_full', crops)
    
    # prepare test data here
    prepare_data('./data/visceral_full', crops, is_train=False)
