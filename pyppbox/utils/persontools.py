# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#   pyppbox: Toolbox for people detecting, tracking, and re-identifying.    #
#   Copyright (C) 2022 UMONS-Numediart                                      #
#                                                                           #
#   This program is free software: you can redistribute it and/or modify    #
#   it under the terms of the GNU General Public License as published by    #
#   the Free Software Foundation, either version 3 of the License, or       #
#   (at your option) any later version.                                     #
#                                                                           #
#   This program is distributed in the hope that it will be useful,         #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#   GNU General Public License for more details.                            #
#                                                                           #
#   You should have received a copy of the GNU General Public License       #
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


from pyppbox.config.unifiedstrings import UnifiedStrings


__ustrings__ = UnifiedStrings()

class Person(object):

    """
    A class used to represent a person.

    Attributes
    ----------
    init_id : int
        Initial ID.
    cid : int
        Current ID.
    box_xywh : ndarray
        Bounding box [x y width height], shape=(4,), dtype=int, ndim=1.
    box_xyxy : ndarray
        Bounding box [x1 y1 x2 y2], shape=(4,), dtype=int, ndim=1.
    keypoints : ndarray
        Keypoints of the body.
    repspoint : tuple(int, int), default=(0, 0)
        Respesented 2D point (x, y).
    det_conf : float, default=0.5
        Confience of detection.
    faceid : str, default="Unknown"
        Face ID.
    deepid : str, default="Unknown"
        Deep ID.
    faceid_conf : float, default=0.0
        Confidence of :attr:`faceid`.
    deepid_conf : float, default=0.0
        Confidence of :attr:`deepid`.
    ontracked : int
        Age of being tracked.

    """

    def __init__(
            self, 
            init_id, 
            cid, 
            box_xywh=[], 
            box_xyxy=[], 
            keypoints=[],
            repspoint=(0, 0), 
            det_conf=0.5,
            faceid=__ustrings__.unk_fid, 
            deepid=__ustrings__.unk_did, 
            fraceid_conf=100.0, 
            deepid_conf=100.0
        ):

        """
        Construct a Person.

        Parameters
        ----------
        init_id : int
            Initial ID.
        cid : int
            Current ID.
        box_xywh : ndarray, optional
            Bounding box :code:`[x y width height]`, :code:`shape=(4,)`, 
            :code:`dtype=int`, :code:`ndim=1`.
        box_xyxy : ndarray, optional
            Bounding box :code:`[x1 y1 x2 y2]`, :code:`shape=(4,)`, 
            :code:`dtype=int`, :code:`ndim=1`.
        keypoints : list[], optional
            Keypoints of the body.
        repspoint : tuple(int, int), default=(0, 0)
            Respesented 2D point (x, y).
        det_conf : float, default=0.5
            Confience of detection.
        faceid : str, default="Unknown"
            Face ID.
        deepid : str, default="Unknown"
            Deep ID.
        faceid_conf : float, default=0.0
            Confidence of :attr:`faceid`.
        deepid_conf : float, default=0.0
            Confidence of :attr:`deepid`.
        ontracked : int, default=0
            Age of being tracked.
        """
        self.init_id = init_id
        self.cid = cid
        self.box_xywh = box_xywh
        self.box_xyxy = box_xyxy
        self.keypoints = keypoints
        self.repspoint = repspoint
        self.det_conf = det_conf
        self.faceid = faceid
        self.deepid = deepid
        self.faceid_conf = fraceid_conf
        self.deepid_conf = deepid_conf
        self.ontracked = 0

    def incrementOnTracked(self):
        """
        Increment ontracked by 1.
        """
        self.ontracked += 1

    def updateOnTracked(self, nframe):
        """
        Update :attr:`ontracked` by the summation of :attr:`ontracked` with :obj:`nframe`.

        Parameters
        ----------
        nframe : int
            Amount of age to be added.
        """
        self.ontracked = self.ontracked + nframe

    def updateIDs(self, new_cid, new_faceid, new_deepid, 
                  new_faceid_conf=0.0, new_deepid_conf=0.0):
        """
        Update :attr:`cid` with :obj:`new_id`, :attr:`faceid` with :obj:`new_faceid`, 
        and :attr:`deepid` with :obj:`new_deepid`.

        Parameters
        ----------
        new_cid : int
            New current ID.
        new_faceid : str
            New face ID.
        new_deepid : str
            New deep ID.
        new_faceid_conf : float, default=0.0
            New confidence of :attr:`faceid`.
        new_deepid_conf :  float, default=0.0
            New confidence of :attr:`deepid`.
        """
        self.cid = new_cid
        self.faceid = new_faceid
        self.deepid = new_deepid
        self.faceid_conf = new_faceid_conf
        self.deepid_conf = new_deepid_conf


#####################################################################################


def findRepspoint(box_xyxy, calibrate_weight):
    """Find respesented point :code:`(x, y)` of a :class:`Person` object by its bounding 
    :code:`box_xyxy` of :code:`[x1 y1 x2 y2]`. The :obj:`calibrate_weight` indicates, 
    in between :code:`min(y1, y2)` and :code:`max(y1, y2)`, where the :code:`y` is.

    Parameters
    ----------
    box_xyxy : ndarray, optional
        Bounding box :code:`[x1 y1 x2 y2]`, :code:`shape=(4,)`, :code:`dtype=int`, 
        :code:`ndim=1`.
    calibrate_weight : float
        Calibration weight.

    Returns
    -------
    tuple(int, int)
        Respesented 2D point :code:`(x, y)`.
    """
    x = int((box_xyxy[0] + box_xyxy[2]) / 2)
    y_start = min(box_xyxy[1], box_xyxy[3])
    y_dist = abs(box_xyxy[1] - box_xyxy[3])
    y = int(y_start + calibrate_weight*y_dist)
    return (x, y)

def findRepspointList(box_xyxy, calibrate_weight):
    """Find respesented point :code:`(x, y)` of a :class:`Person` object by its bounding 
    :code:`box_xyxy` of :code:`[x1 y1 x2 y2]`. The :obj:`calibrate_weight` indicates, 
    in between :code:`min(y1, y2)` and :code:`max(y1, y2)`, where the :code:`y` is.

    Parameters
    ----------
    box_xyxy : ndarray, optional
        Bounding box :code:`[x1 y1 x2 y2]`, :code:`shape=(4,)`, :code:`dtype=int`, 
        :code:`ndim=1`.
    calibrate_weight : float
        Calibration weight.

    Returns
    -------
    list[int, int]
        Respesented 2D point :code:`[x, y]`.
    """
    x = int((box_xyxy[0] + box_xyxy[2]) / 2)
    y_start = min(box_xyxy[1], box_xyxy[3])
    y_dist = abs(box_xyxy[1] - box_xyxy[3])
    y = int(y_start + calibrate_weight*y_dist)
    return [x, y]