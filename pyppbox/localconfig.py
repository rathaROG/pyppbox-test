"""
    pyppbox: Toolbox for people detecting, tracking, and re-identifying.
    Copyright (C) 2022 UMONS-Numediart

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


from __future__ import division, print_function, absolute_import

import os
import cv2
import yaml

from yaml.loader import SafeLoader
from .utils.deepreid_model_dict import ModelDictionary
from .utils.mystrings import MyStrings
from .utils.mytools import getFileName, joinFPathFull, normalizePathFDS, getAbsPathFDS, getAncestorDir, customDumpSingleDoc, customDumpMultiDoc

global_root_dir = os.path.dirname(__file__)
global_cfg_dir = joinFPathFull(global_root_dir, 'cfg')

class MyLocalStruct(object):

    def __init__(self, cfg_dir):
        self.cfg_dir = cfg_dir
        self.global_root_dir = global_root_dir
        self.loadDIR()
        self.loadYAML()
        self.loadSTR()
        self.loadVS()

    def loadDIR(self):
        self.tmp_dir = os.path.join(global_root_dir, 'tmp')
        self.gt_dir = os.path.join(self.tmp_dir, 'gt')
        self.res_dir = os.path.join(self.tmp_dir, 'res')

    def loadYAML(self):
        self.main_yaml = os.path.join(self.cfg_dir, "main.yaml")
        self.detector_yaml = os.path.join(self.cfg_dir, "detectors.yaml")
        self.tracker_yaml = os.path.join(self.cfg_dir, "trackers.yaml")
        self.reider_yaml = os.path.join(self.cfg_dir, "reiders.yaml")
        self.string_yaml = os.path.join(global_cfg_dir, "strings.yaml")

    def loadSTR(self):
        self.str = MyStrings(self.string_yaml)

    def loadVS(self):
        self.vp = (150, 30)
        self.vp_reid =  (325, 30)
        self.vp_co = (0, 255, 0)
        self.vp_sp = " "
        self.vp_font = cv2.FONT_HERSHEY_COMPLEX_SMALL


################################################################################################################


class DCFGYOLO(object):

    def __init__(self):
        pass

    def set(self, dcfg):
        self.dt_name = dcfg['dt_name']
        self.nms_threshold = dcfg['nms_threshold']
        self.conf_threshold = dcfg['conf_threshold']
        self.class_file = getAbsPathFDS(dcfg['class_file'])
        self.model_cfg_file = getAbsPathFDS(dcfg['model_cfg_file'])
        self.model_weights = getAbsPathFDS(dcfg['model_weights'])
        self.model_resolution = (dcfg['model_resolution_width'], dcfg['model_resolution_height'])
        self.repspoint_callibration = dcfg['repspoint_callibration']

    def getDocument(self):
        (w, h) = self.model_resolution
        yolo_doc = {"dt_name": "YOLO",
                    "nms_threshold": self.nms_threshold,
                    "conf_threshold": self.conf_threshold,
                    "class_file": getAbsPathFDS(self.class_file),
                    "model_cfg_file": getAbsPathFDS(self.model_cfg_file),
                    "model_weights": getAbsPathFDS(self.model_weights),
                    "model_resolution_width": w,
                    "model_resolution_height": h,
                    "repspoint_callibration": self.repspoint_callibration}
        return yolo_doc


class DCFGGT(object):

    def __init__(self):
        pass

    def set(self, dcfg):
        self.dt_name = dcfg['dt_name']
        self.gt_file = joinFPathFull(global_root_dir, dcfg['gt_file'])
        self.input_gt_map_file = joinFPathFull(global_root_dir, dcfg['input_gt_map_file'])

    def getDocument(self):
        gt_doc = {"dt_name": "GT",
                  "gt_file": normalizePathFDS(global_root_dir, self.gt_file),
                  "input_gt_map_file": normalizePathFDS(global_root_dir, self.input_gt_map_file)}
        return gt_doc


class TCFGCentroid(object):

    def __init__(self):
        pass

    def set(self, tcfg):
        self.tk_name = tcfg['tk_name']
        self.max_distance = tcfg['max_distance']

    def getDocument(self):
        centroid_doc = {"tk_name": "Centroid",
                        "max_distance": self.max_distance}
        return centroid_doc


class TCFGSORT(object):

    def __init__(self):
        pass

    def set(self, tcfg):
        self.tk_name = tcfg['tk_name']
        self.max_age = tcfg['max_age']
        self.min_hits = tcfg['min_hits']
        self.iou_threshold = tcfg['iou_threshold']

    def getDocument(self):
        sort_doc = {"tk_name": "SORT",
                    "max_age": self.max_age,
                    "min_hits": self.min_hits,
                    "iou_threshold": self.iou_threshold}
        return sort_doc
        

class TCFGDeepSORT(object):

    def __init__(self):
        pass

    def set(self, tcfg):
        self.tk_name = tcfg['tk_name']
        self.nn_budget = tcfg['nn_budget']
        self.nms_max_overlap = tcfg['nms_max_overlap']
        self.max_cosine_distance = tcfg['max_cosine_distance']
        self.model_file = getAbsPathFDS(tcfg['model_file'])

    def getDocument(self):
        deepsort_doc = {"tk_name": "DeepSORT",
                        "nn_budget": self.nn_budget,
                        "nms_max_overlap": self.nms_max_overlap,
                        "max_cosine_distance": self.max_cosine_distance,
                        "model_file": getAbsPathFDS(self.model_file)}
        return deepsort_doc


class RCFGFacenet(object):

    def __init__(self):
        pass

    def set(self, rcfg):
        self.ri_name = rcfg['ri_name']
        self.gpu_mem = rcfg['gpu_mem']
        self.model_det = getAbsPathFDS(rcfg['model_det'])
        self.model_file = getAbsPathFDS(rcfg['model_file'])
        self.classifier_file = getAbsPathFDS(rcfg['classifier_file'])
        self.batch_size = rcfg['batch_size']
        self.min_confidence = rcfg['min_confidence']
        self.yl_h_callibration = rcfg['yl_h_callibration']
        self.yl_w_callibration = rcfg['yl_w_callibration']
        self.op_h_callibration = rcfg['op_h_callibration']
        self.op_w_callibration = rcfg['op_w_callibration']

    def getDocument(self):
        facenet_doc = {"ri_name": "Facenet",
                        "gpu_mem": self.gpu_mem,
                        "model_det": getAbsPathFDS(self.model_det), 
                        "model_file": getAbsPathFDS(self.model_file),
                        "classifier_file": getAbsPathFDS(self.classifier_file),
                        "batch_size": self.batch_size,
                        "min_confidence": self.min_confidence,
                        "yl_h_callibration": self.yl_h_callibration,
                        "yl_w_callibration": self.yl_w_callibration,
                        "op_h_callibration": self.op_h_callibration,
                        "op_w_callibration": self.op_w_callibration}
        return facenet_doc


class RCFGDeepReID(object):

    def __init__(self, mstruct):
        self.mstruct = mstruct

    def set(self, rcfg):
        self.ri_name = rcfg['ri_name']
        self.classes_txt = getAbsPathFDS(rcfg['classes_txt'])
        self.classifier_pkl = getAbsPathFDS(rcfg['classifier_pkl'])
        self.train_data = getAbsPathFDS(rcfg['train_data'])
        self.model_name = rcfg['model_name']
        self.model_path = getAbsPathFDS(rcfg['model_path'])
        self.min_confidence = rcfg['min_confidence']
        self.setExtra()
    
    def setExtra(self):
        self.base_model_path = getAbsPathFDS(os.path.join(getAncestorDir(self.model_path, 1), 'base'))
        self.unk_did = self.mstruct.str.unk_did
        self.err_did = self.mstruct.str.err_did

    def getDocument(self):
        deepreid_doc = {"ri_name": "DeepReID",
                       "classes_txt": getAbsPathFDS(self.classes_txt),
                       "classifier_pkl": getAbsPathFDS(self.classifier_pkl),
                       "train_data": getAbsPathFDS(self.train_data),
                       "model_name": self.model_name,
                       "model_path": getAbsPathFDS(self.model_path),
                       "min_confidence": self.min_confidence}
        return deepreid_doc


class MainCFG(object):

    def __init__(self):
        pass

    def set(self, mcfg):
        self.detector = mcfg['detector']
        self.tracker = mcfg['tracker']
        self.reider = mcfg['reider']
        self.input_video = mcfg['input_video']
        self.force_hd = mcfg['force_hd']


class MyLocalConfigurator(object):

    def __init__(self, local_cfg_dir):
        self.cfgio = MyCFGIO(local_cfg_dir)
        self.mstruct = self.cfgio.getMStruct()
        self.mcfg = MainCFG()
        self.dcfg_yolo = DCFGYOLO()
        self.dcfg_gt = DCFGGT()
        self.tcfg_centroid = TCFGCentroid()
        self.tcfg_sort = TCFGSORT()
        self.tcfg_deepsort = TCFGDeepSORT()
        self.rcfg_facenet = RCFGFacenet()
        self.rcfg_deepreid = RCFGDeepReID(mstruct=self.mstruct)

    def loadMCFG(self):
        data = self.cfgio.loadDocument(self.mstruct.main_yaml)
        self.mcfg.set(data)

    def loadDCFG(self):
        docs = self.cfgio.loadAllDocuments(self.mstruct.detector_yaml)
        for d in docs:
            if d['dt_name'].lower() == "yolo":
                self.dcfg_yolo.set(d)
            elif d['dt_name'].lower() == "gt":
                self.dcfg_gt.set(d)

    def loadTCFG(self):
        docs = self.cfgio.loadAllDocuments(self.mstruct.tracker_yaml)
        for d in docs:
            if d['tk_name'].lower() == "centroid":
                self.tcfg_centroid.set(d)
            elif d['tk_name'].lower() == "sort":
                self.tcfg_sort.set(d)
            elif d['tk_name'].lower() == "deepsort":
                self.tcfg_deepsort.set(d)

    def loadRCFG(self):
        docs = self.cfgio.loadAllDocuments(self.mstruct.reider_yaml)
        for d in docs:
            if d['ri_name'].lower() == "facenet":
                self.rcfg_facenet.set(d)
            elif d['ri_name'].lower() == "deepreid":
                self.rcfg_deepreid.set(d)
        self.loadExtra()

    def loadExtra(self):
        self.dr_md = ModelDictionary()
        self.dr_md.loadCFG(joinFPathFull(global_cfg_dir, 'deepreid_model_dict.yaml'))
        self.dr_wh = self.dr_md.getWH(getFileName(self.rcfg_deepreid.model_path))


class MyCFGHeaderNote(object):

    def __init__(self):
        pass

    def mainHeader(self):
        header=("###########################################################\n"
                "# Main config:\n"
                "###########################################################\n"
                "# detector: None | YOLO\n"
                "# tracker: None | Centroid | SORT | DeepSORT\n"
                "# reider: None | Facenet | DeepReID\n"
                "# input_video: *.avi | *.mkv | *.mov | *.mp4\n"
                "# force_hd: True | False\n"
                "###########################################################\n")
        return header

    def detectorHeader(self):
        header=("###########################################################\n"
                "# Detector config:\n"
                "###########################################################\n"
                "# --- # YOLO\n"
                "# dt_name: YOLO\n"
                "# nms_threshold: 0.45\n"
                "# conf_threshold: 0.5\n"
                "# class_file: dt_yolocv/coco.names\n"
                "# model_cfg_file: dt_yolocv/yolov4.cfg\n"
                "# model_weights: dt_yolocv/yolov4.weights\n"
                "# model_resolution_width: 416\n"
                "# model_resolution_height: 416\n"
                "# repspoint_callibration: 0.25\n"
                "###########################################################\n"
                "# --- # GT aka Ground Truth\n"
                "# dt_name: GT\n"
                "# gt_file: tmp/gt/realID_hard_sur.txt\n"
                "# input_gt_map_file: tmp/gt/input_gt_map.txt\n"
                "###########################################################\n")
        return header

    def trackerHeader(self):
        header=("###########################################################\n"
                "# Tracker config:\n"
                "###########################################################\n"
                "# --- # Centroid\n"
                "# tk_name: Centroid\n"
                "# max_distance: 50\n"
                "###########################################################\n"
                "# --- # SORT\n"
                "# tk_name: SORT\n"
                "# max_age: 1\n"
                "# min_hits: 3\n"
                "# iou_threshold: 0.3\n"
                "###########################################################\n"
                "# --- # DeepSORT\n"
                "# tk_name: DeepSORT\n"
                "# nn_budget: 100\n"
                "# nms_max_overlap: 0.5\n"
                "# max_cosine_distance: 0.1\n"
                "# model_file: tk_deepsort/mars-small128.pb\n"
                "###########################################################\n")
        return header

    def reiderHeader(self):
        header=("###########################################################\n"
                "# ReIDer config:\n"
                "###########################################################\n"
                "# --- # Facenet\n"
                "# ri_name: Facenet\n"
                "# gpu_mem: 0.585\n"
                "# model_det: ri_facenet/models/det\n"
                "# model_file: ri_facenet/models/20180402-114759/20180402-114759.pb\n"
                "# classifier_file: ri_facenet/classifier/train.pkl\n"
                "# batch_size: 1000\n"
                "# min_confidence: 0.75\n"
                "# yl_h_callibration: [-125, 75]\n"
                "# yl_w_callibration: [-55, 55]\n"
                "# op_h_callibration: [-85, 25]\n"
                "# op_w_callibration: [-35, 35]\n"
                "###########################################################\n"
                "# --- # DeepReID\n"
                "# ri_name: DeepReID\n"
                "# classes_txt: ri_deepreid/classifier/gta5.txt\n"
                "# classifier_pkl: ri_deepreid/classifier/gta5_mlfn.pkl\n"
                "# train_data: ri_deepreid/data\n"
                "# model_name: mlfn\n"
                "# model_path: ri_deepreid/pretrained/base/mlfn-9cb5a267.pth.tar\n"
                "# min_confidence: 0.35\n"
                "###########################################################\n")
        return header

    def copyrightCMDHeader(self):
        header=("::    pyppbox: Toolbox for people detecting, tracking, and re-identifying.\n"
                "::    Copyright (C) 2022 UMONS-Numediart\n"
                "::\n"
                "::    This program is free software: you can redistribute it and/or modify\n"
                "::    it under the terms of the GNU General Public License as published by\n"
                "::    the Free Software Foundation, either version 3 of the License, or\n"
                "::    (at your option) any later version.\n"
                "::\n"
                "::    This program is distributed in the hope that it will be useful,\n"
                "::    but WITHOUT ANY WARRANTY; without even the implied warranty of\n"
                "::    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n"
                "::    GNU General Public License for more details.\n"
                "::\n"
                "::    You should have received a copy of the GNU General Public License\n"
                "::    along with this program.  If not, see <https://www.gnu.org/licenses/>.\n\n\n")
        return header


class MyCFGIO(object):

    def __init__(self, local_cfg_dir):
        self.mstruct = MyLocalStruct(local_cfg_dir)
        self.headers = MyCFGHeaderNote()

    def getMStruct(self):
        return self.mstruct

    def loadDocument(self, cfg_yaml):
        data = []
        with open(cfg_yaml, 'r') as cfg:
            data = yaml.load(cfg, Loader=SafeLoader)
        return data

    def loadAllDocuments(self, cfg_yaml):
        documents = []
        with open(cfg_yaml, 'r') as cfg:
            docs = yaml.load_all(cfg, Loader=SafeLoader)
            for doc in docs:
                documents.append(doc)
        return documents

    def dumpMainWithHeader(self, data):
        customDumpSingleDoc(self.mstruct.main_yaml, data, self.headers.mainHeader())

    def dumpDetectorsWithHeader(self, documents):
        customDumpMultiDoc(self.mstruct.detector_yaml, documents, self.headers.detectorHeader())

    def dumpTrackersWithHeader(self, documents):
        customDumpMultiDoc(self.mstruct.tracker_yaml, documents, self.headers.trackerHeader())

    def dumpReidersWithHeader(self, documents):
        customDumpMultiDoc(self.mstruct.reider_yaml, documents, self.headers.reiderHeader())
