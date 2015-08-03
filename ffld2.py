import menpo.io as mio
from utils import (mkdir_p, check_if_path, print_fancy, Logger)
from utils.path_and_folder_definition import *  # import paths for databases, folders and libraries
from utils.pipeline_aux import (check_img_type, im_read_greyscale, check_initial_path, check_path_and_landmarks, load_images)
from utils.clip import Clip
import numpy as np
from menpo.shape import PointCloud
from joblib import Parallel, delayed
from menpodetect.ffld2 import FFLD2Detector, train_ffld2_detector
from menpodetect.dlib.conversion import pointgraph_to_rect
from menpo.landmark import LandmarkGroup
import dlib
from cyffld2 import load_model


if __name__ == '__main__':
    args = len(sys.argv)
    path_clips = check_initial_path(args, sys.argv)

    if 2 < args < 7:
        in_bb_fol = str(sys.argv[2]) + sep
        out_bb_fol = str(sys.argv[3]) + sep
        out_model_fol = str(sys.argv[4]) + sep
        out_landmarks_fol = str(sys.argv[5]) + sep
        print in_bb_fol, '   ', out_landmarks_fol
    else:
        in_bb_fol = '1_dlib_detect' + sep
        out_bb_fol, out_model_fol, out_landmarks_fol = '2_ffld' + sep, '2_ffld_models' + sep, '3_ffld_ln' + sep


p_det_0 = path_clips + out_bb_fol
p_det_1 = path_clips + out_landmarks_fol
p_det_bb_0 = path_clips + in_bb_fol  # existing bbox of detection
p_save_model = mkdir_p(path_clips + out_model_fol)  # path that trained models will be saved
overwrite = False


import datetime
log = mkdir_p(path_clips + 'logs' + sep) + datetime.datetime.now().strftime("%Y.%m.%d.%H.%M.%S") + '_2_ffld_verification.log'
sys.stdout = Logger(log)


predictor_dlib = dlib.shape_predictor(path_shape_pred)

def detection_to_pointgraph(detection):
    return PointCloud(np.array([(p.y, p.x) for p in detection.parts()]))

    
def predict_in_frame(frame_name, clip):
    global detector
    im = im_read_greyscale(frame_name, clip.path_frames, img_type, normalise=False)

    res_dlib = detector(im)
    num_res = len(res_dlib)
    if num_res == 0:
        return
    num1 = 1                # num1 and s1: Values if there are more than 10 detections in the image
    if num_res > 9:
        num1 = 2
    s1 = '%0' + str(num1)
    im_pili = np.array(im.as_PILImage())
    for kk in range(0, 1):   # num_res to keep all, here keeping ONLY the most confident one
        pts_end = im.path.stem + '_' + str(kk) + pts_type_out
        ln = im.landmarks['ffld2_' + (s1 + 'd') % kk]
        mio.export_landmark_file(ln, clip.path_write_ln[0] + pts_end, overwrite=True)
        # convert to landmarks
        det_frame = predictor_dlib(im_pili, pointgraph_to_rect(ln.lms))
        init_pc = detection_to_pointgraph(det_frame)
        mio.export_landmark_file(LandmarkGroup.init_with_all_label(init_pc), clip.path_write_ln[1] + pts_end, overwrite=True)



negative_images = [i.as_greyscale(mode='channel', channel=1) for i in mio.import_images('/vol/atlas/homes/pts08/non_person_images',normalise=False, max_images=300)]
detector = []
def process_clip(clip_name, overwrite=True):
    # overwrite: overwrite the training of the FFLD model.
    print clip_name
    frames_path = path_clips + frames + clip_name + sep
    if not check_path_and_landmarks(frames_path, clip_name, p_det_bb_0 + clip_name + sep):  # check that paths, landmarks exist
        return

    list_frames = sorted(os.listdir(frames_path))
    save_model = p_save_model + clip_name + '.model'
    if (not os.path.exists(save_model)) or overwrite:
        # build the detector
        training_pos = load_images(list_frames, frames_path, p_det_bb_0, clip_name, max_images=400)
        if len(training_pos) == 0:
            print('No positives found for the clip %s, skipping it.' % clip_name)
            return
        ps_model = train_ffld2_detector(training_pos, negative_images, n_components=1, n_relabel=6)
        ps_model.save(save_model)
    else:
        print('The model {} already exists and was loaded from disk.'.format(save_model))
        ps_model = load_model(save_model)
    global detector
    detector = FFLD2Detector(ps_model)

    p_det_bb = mkdir_p(p_det_0 + clip_name + sep)
    p_det_landm = mkdir_p(p_det_1 + clip_name + sep)
    clip = Clip(clip_name, path_clips, frames, write_ln=[p_det_bb, p_det_landm])
    # TODO: Try parallel model
    [predict_in_frame(frame_name, clip) for frame_name in list_frames]

print_fancy('Training person specific model with FFLD')
list_clips = sorted(os.listdir(path_clips + frames))
img_type = check_img_type(list_clips, path_clips + frames)  # assumption that all clips have the same extension, otherwise run in the loop for each clip separately.
[process_clip(clip_name, overwrite=overwrite) for clip_name in list_clips];


