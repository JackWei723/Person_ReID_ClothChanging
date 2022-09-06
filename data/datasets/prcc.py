# encoding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import glob
import os.path as osp
import numpy as np


class BaseDataset(object):
    """
    Base class of reid dataset
    """

    def get_imagedata_info(self, data):
        pids, cams = [], []
        for _, pid, camid in data:
            pids += [pid]
            cams += [camid]
        pids = set(pids)
        cams = set(cams)
        num_pids = len(pids)
        num_cams = len(cams)
        num_imgs = len(data)
        return num_pids, num_imgs, num_cams

    def get_videodata_info(self, data, return_tracklet_info=False):
        pids, cams, tracklet_info = [], [], []
        for img_paths, pid, camid in data:
            pids += [pid]
            cams += [camid]
            tracklet_info += [len(img_paths)]
        pids = set(pids)
        cams = set(cams)
        num_pids = len(pids)
        num_cams = len(cams)
        num_tracklets = len(data)
        if return_tracklet_info:
            return num_pids, num_tracklets, num_cams, tracklet_info
        return num_pids, num_tracklets, num_cams

    def print_dataset_statistics(self):
        raise NotImplementedError



class PRCC(BaseDataset):
    """
      --------------------------------------
      subset         | # ids     | # images
      --------------------------------------
      train          |   150     |    17896
      query          |    71     |      213
      gallery        |    71     |    10587
    """
    dataset_dir = 'modify'
    cam2label = {'A': 0, 'B': 1, 'C': 2}

    def __init__(self, root='data', verbose=True, **kwargs):
        super(PRCC, self).__init__()
        self.dataset_dir = osp.join(root, self.dataset_dir)
        self.train_dir = osp.join(self.dataset_dir, 'train')
        self.query_dir = osp.join(self.dataset_dir, 'test', 'query')
        self.gallery_dir = osp.join(self.dataset_dir, 'test', 'gallery')

        self._check_before_run()

        self.pid2label = self.get_pid2label(self.train_dir)
        self.train = self._process_dir(self.train_dir, pid2label=self.pid2label, relabel=True)          # 13081
        self.query = self._process_dir(self.query_dir, relabel=False)       # 484
        self.gallery = self._process_dir(self.gallery_dir, relabel=False)

        if verbose:
            print("=> PRCC loaded")
            self.print_dataset_statistics_movie(self.train, self.query, self.gallery)

        self.num_train_pids, self.num_train_imgs, self.num_train_cams = self.get_imagedata_info(self.train)
        self.num_query_pids, self.num_query_imgs, self.num_query_cams = self.get_imagedata_info(self.query)
        self.num_gallery_pids, self.num_gallery_imgs, self.num_gallery_cams = self.get_imagedata_info(self.gallery)


    def get_pid2label(self, dir_path):
        persons = os.listdir(dir_path)
        pid_container = np.sort(list(set(persons)))
        pid2label = {pid: label for label, pid in enumerate(pid_container)}
        return pid2label

    def _check_before_run(self):
        """Check if all files are available before going deeper"""
        if not osp.exists(self.dataset_dir):
            raise RuntimeError("'{}' is not available".format(self.dataset_dir))
        if not osp.exists(self.train_dir):
            raise RuntimeError("'{}' is not available".format(self.train_dir))
        if not osp.exists(self.query_dir):
            raise RuntimeError("'{}' is not available".format(self.query_dir))
        if not osp.exists(self.gallery_dir):
            raise RuntimeError("'{}' is not available".format(self.gallery_dir))

    def _process_dir(self, dir_path, pid2label=None, relabel=False):
        persons = os.listdir(dir_path)
        dataset = []
        for pid_s in persons:
            path_p = os.path.join(dir_path, pid_s)
            files = os.listdir(path_p)
            for file in files:
                cid = file.split('_')[0]
                cid = self.cam2label[cid]
                if relabel and pid2label is not None:
                    pid = pid2label[pid_s]
                else:
                    pid = int(pid_s)
                img_path = os.path.join(dir_path, pid_s, file)
                dataset.append((img_path, pid, cid))
        return dataset


    def print_dataset_statistics_movie(self, train, query, gallery):
        num_train_pids, num_train_imgs, num_train_cams = self.get_imagedata_info(train)
        num_query_pids, num_query_imgs, num_query_cams = self.get_imagedata_info(query)
        num_gallery_pids, num_gallery_imgs, num_gallery_cams = self.get_imagedata_info(gallery)

        print("Dataset statistics:")
        print("  --------------------------------------")
        print("  subset         | # ids     | # images")
        print("  --------------------------------------")
        print("  train          | {:5d}     | {:8d}".format(num_train_pids, num_train_imgs))
        print("  query          | {:5d}     | {:8d}".format(num_query_pids, num_query_imgs))
        print("  gallery        | {:5d}     | {:8d}".format(num_gallery_pids, num_gallery_imgs))


