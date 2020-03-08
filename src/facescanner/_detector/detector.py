from collections import namedtuple
from typing import List

import numpy as np
import tensorflow as tf

from src import _pyutils
from src.facescanner._detector._lib.align import detect_face
from src.facescanner._detector.constants import SCALE_FACTOR, DEFAULT_THRESHOLD_A, DEFAULT_THRESHOLD_B, \
    DEFAULT_THRESHOLD_C, FaceLimitConstant, BOX_MARGIN, FACE_MIN_SIZE
from src.facescanner._detector.exceptions import NoFaceFoundError
from src.facescanner.dto.bounding_box import BoundingBox


FaceDetectionNets = namedtuple('FaceDetectionNets', 'pnet rnet onet')


@_pyutils.run_once
def _face_detection_nets():
    with tf.Graph().as_default():
        sess = tf.Session()
        return FaceDetectionNets(*detect_face.create_mtcnn(sess, None))


def find_face_bounding_boxes(img, face_limit=FaceLimitConstant.NO_LIMIT, detection_threshold_c=DEFAULT_THRESHOLD_C) \
        -> List[BoundingBox]:
    fdn = _face_detection_nets()
    detect_face_result = detect_face.detect_face(img, FACE_MIN_SIZE, fdn.pnet, fdn.rnet, fdn.onet,
                                                 [DEFAULT_THRESHOLD_A, DEFAULT_THRESHOLD_B, detection_threshold_c],
                                                 SCALE_FACTOR)
    img_size = np.asarray(img.shape)[0:2]
    bounding_boxes = []
    for result_item in detect_face_result[0]:
        result_item = np.squeeze(result_item)
        margin = BOX_MARGIN / 2
        bounding_box = BoundingBox(
            x_min=int(np.maximum(result_item[0] - margin, 0)),
            y_min=int(np.maximum(result_item[1] - margin, 0)),
            x_max=int(np.minimum(result_item[2] + margin, img_size[1])),
            y_max=int(np.minimum(result_item[3] + margin, img_size[0])),
            probability=result_item[4]
        )
        bounding_boxes.append(bounding_box)

    if len(bounding_boxes) < 1:
        raise NoFaceFoundError("No face is found in the given image")
    if face_limit:
        return bounding_boxes[:face_limit]
    return bounding_boxes
