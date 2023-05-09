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


import os
import sys
import cv2
import imutils.video
import pyppbox

from timeit import time
from pyppbox.ppboxmng import PManager

#####################################################################################
# IMPORTANT CHANGES FROM v1.1
#####################################################################################
# - PManager() now has the default __init__(enableEval=False, localConfig=False).
# - The "localConfig=False" means PManager uses the GLOBAL "cfg" dir inside the 
#   pyppbox package.
# - When "localConfig=True", you must call "setLocalConfig(local_cfg_dir)" in order 
#   to set your new LOCAL "cfg" dir.
# - The idea of GLOBAL & LOCAL enables pyppbox to be used in multi-threading without 
#   inteferring with the GLOBAL "cfg" dir.
# - More info, please visit https://github.com/rathaumons/pyppbox/tree/main/examples
#####################################################################################

# Show main config
pyppbox.showMainCFG()

# Set input video
# pyppbox.setInputVideo('C:/media/hard_sur_hd.mp4')

# Set config for all detector
'''
detectors_config = [
    {
        'dt_name': 'YOLO', 
        'nms_threshold': 0.45, 
        'conf_threshold': 0.5, 
        'class_file': 'dt_yolocv/coco.names', 
        'model_cfg_file': 'dt_yolocv/yolov4.cfg', 
        'model_weights': 'dt_yolocv/yolov4.weights', 
        'model_resolution_width': 416, 
        'model_resolution_height': 416, 
        'repspoint_callibration': 0.25
    },
    {
        'dt_name': 'YOLO_Ultralytics', 
        'conf': 0.5, 
        'iou': 0.7, 
        'imgsz': 416, 
        'classes': 0, 
        'boxes': True, 
        'device': 0, 
        'max_det': 100, 
        'hide_labels': True, 
        'hide_conf': True, 
        'line_width': 500, 
        'visualize': False, 
        'model_file': 'dt_yolopt/yolov8l-pose.pt', 
        'repspoint_callibration': 0.25
    }, 
    {
        'dt_name': 'GT', 
        'gt_file': 'tmp/gt/realID_hard_sur.txt', 
        'input_gt_map_file': 'tmp/gt/input_gt_map.txt'
    }
]
pyppbox.setDetectorsCFG(detectors_config)
'''

# Set main config
main_config = {
    'detector': 'YOLO_Ultralytics', 
    'tracker': 'SORT', 
    'reider': 'DeepReID', 
    'input_video': 'C:/media/hard_sur_hd.mp4', 
    'force_hd': False
}
pyppbox.setMainCFG(main_config)

# Luanch GUI
# pyppbox.launchGUI()


try:

    pmg = PManager(enableEval=True)
    
    input_source = pmg.getInputFile()
    print("Input video: " + str(input_source))
    
    cap = cv2.VideoCapture(input_source)
    cap_width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    cap_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Screenshot a frame for offline EVA-IO
    screenshot = []
    screenshot_at = 60

    fps = 0.0
    fps_imutils = imutils.video.FPS().start()

    # Need frame_id for display & offline EVA-IO
    frame_id = 0

    # Start video
    while cap.isOpened():
        t1 = time.time()
        hasFrame, frame = cap.read()
        if hasFrame:

            # Resize frame if force HD
            if pmg.forceHD(): frame = cv2.resize(frame, (1280, int((1280/cap_width) * cap_height)))

            # Update detecter
            ppobl = pmg.detectFramePPOBL(frame, True)

            # Update tracker
            pmg.updateTrackerPPOBL(ppobl)

            # Call reider
            pmg.reidNormal()        # Level 1: normal
            pmg.reidDupkiller()     # Level 2: dupkiller

            # Display info
            updated_pp = pmg.getCurrentPPOBL()
            det_frame = pmg.getFrameVisual()
            for person in updated_pp:
                (x, y) = person.getRepspoint()
                cv2.putText(det_frame, str(person.getCid()), (int(x - 10), int(y - 60)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.putText(det_frame, str(person.getDeepid()), (int(x - 85), int(y - 90)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 200, 0), 2)
                cv2.putText(det_frame, str(person.getFaceid()), (int(x - 85), int(y - 125)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                # Add tracked person to the offline EVA-IO
                pmg.eva_io.add_person(frame_id, person, mode=pmg.evalmode)

            # Update online realtime EVA-RT frame by frame
            pmg.selfRealtimeEval()

            # Add framerate & info
            fps_imutils.update()
            fps = (fps + (1./((1.000000000001*time.time())-t1))) / 2
            cv2.putText(det_frame, str(int(fps)) + " | " + str(frame_id), (15, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow("pyppbox Demo", det_frame)

            # Take a screenshot
            if screenshot_at == frame_id:
                screenshot = det_frame.copy()

            frame_id += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        else:
            break
    
    cap.release()

    # Online realtime EVA-RT
    # Note: Realtime EVA-RT only supports faceid and deepid on GTA V dataset
    pmg.getRealtimeEvalResult()

    # Offline EVA-IO
    # Note: only supports faceid and deepid on PoseTReID dataset
    res_txt, extra_info = pmg.generateExtraInfoForOfflineEva()
    docs_path = os.path.expanduser('~/Documents/pyppbox')
    if not os.path.exists(docs_path): os.makedirs(docs_path)

    res_txt = os.path.join(docs_path, res_txt)
    pmg.eva_io.dump(res_txt)

    screenshot_jpg = res_txt[:-4] + "_info.jpg"
    cv2.imwrite(screenshot_jpg, screenshot)

    info_txt = res_txt[:-4] + "_info.txt"
    with open(info_txt, "a") as info_file:
        info_file.write(extra_info)

    print("\nMore info was saved to " + str(docs_path) + str("\n"))


except Exception as e:
    print(e)
    sys.exit(-1)

