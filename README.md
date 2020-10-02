
This is the code accompanying the paper [`Offline Deformable Face Tracking in Arbitrary Videos`, ICCV 2015 Workshops.](http://ibug.doc.ic.ac.uk/media/uploads/documents/paper_offline.pdf)
To use the code you can call the whole pipeline by calling the run_pipeline.py with the path of the videos.
Probably you need to adapt the paths in `utils/path_and_folder_definition.py` to fit your system.

#### **Folder structure**
The pipeline proposed assumes the following folder structure:

```
path_base
    │
    └───frames
            │
            └───[name_of_clip]
                    │ [frame_name].[extension] (e.g. 000001.png)
                    │ [frame_name].[extension] (e.g. 000002.png)
                    │ ...
            │ ...
    │
    └───gt_landmarks  (not required for executing the code)
            │
            └───[name_of_clip]
                    │ [file_name].[extension] (e.g. 000001.pts)
                    │ ...
            │ ...
```

In the `example_folder_structure/` the structure as described above can be found. 
The scripts will iteratively run for all clips in the `frames/` folder. 


Explanation of the different pipeline files:

* dlib_predictor.py: Uses pre-trained (generic) detector to detect the bounding box of the face and then applies a shape predictor/regressor (from dlib).
* ffld2.py: Trains a person specific detector. It utilises the input bounding boxes of the previous step to train the model and then detects using that model. Additionally, it applies the same shape predictor as in dlib_predictor.py.
* ps_pbaam.py: Trains a generic + adaptive part-based AAM and then fits it on the person.


If you run run_pipeline.py:

A number of frames are expected to be found for each video with potentially one person showing in these videos. For the frames that a person is found, a pts file will be exported per frame. That is, for each step there will be a pts exported for comparison reasons. 

If more people appear in the video, then this might cause confusion in the person specific models, since there is no prediction over spatial consistency, most of the steps rely on the most confident detection.


The pipeline includes the following steps:

1) A generic face detector is run in a batch of clips. (Additionally, the landmarks of a generic land. loc. method are exported, but this is auxiliary). 

2) A person specific detector is trained and fit in each clip. Based on that acquired bounding box, a generic landmark localisation method is applied. 

3) Using the landmarks from the previous step, a person specific landmark localisation method (AAM) is trained and fit in the landmarks. (Optionally use an SVM as a failure checking method). 

4) Re-train 3 with the improved landmarks and optionally apply the failure checker again. 

#### **Dependency**
Apart from menpo [(menpo, menpodetect, menpofit)](https://github.com/menpo/menpo) the following packages are used:
* joblib ``` pip install joblib```
* research_pyutils from [this repository](https://github.com/grigorisg9gr/pyutils).

Additionally, for the predictor in the dlib_predictor.py, you need to provide a pre-trained model for landmark localisation. You can optionally provide a path with a pre-trained SVM to work as a failure checker in the ps_pbaam.py part. 

#### **Feedback**
If you do have any questions or improvements, feel free to open issues here or contribute right away. Feedback is always appreciated.
Due to the heavy development of menpo and its research purpose, often there are breaking changes. This code, may not work with the latest menpoversion, however if you encounter such a compatibility problem, please get in touch and I will fix the problem with the code.

#### **License**
Apache 2, see LICENSE file for more details.
