Notes from Ravi: 
Phase-1:
multile cameras to one object detection 
multiple sensor to one object detection 
multi camera - guasssion splatting --> lidar and other sensors 
sensor fusion thing 

----------------------------------------------------------
About Data 
----------------------------------------------------------
calibration
	camera_intrinsics /camera_intrinsics.chunk_0000.parquet
	sensor_extrinsics /sensor_extrinsics.chunk_0000.parquet
	vehicle_dimensions /vehicle_dimensions.chunk_0000.parquet

camera
	camera_cross_left_120fov / camera_cross_left_120fov.chunk_0000.zip
    camera_cross_right_120fov /camera_cross_right_120fov.chunk_0000.zip
    camera_front_tele_30fov / camera_front_tele_30fov.chunk_0000.zip
    camera_front_wide_120fov /camera_front_wide_120fov.chunk_0000.zip
    camera_rear_left_70fov /camera_rear_left_70fov.chunk_0000.zip
    camera_rear_right_70fov / camera_rear_right_70fov.chunk_0000.zip
	camera_rear_tele_30fov / camera_rear_tele_30fov.chunk_0000.zip

labels
    egomotion / egomotion.chunk_0000.zip

lidar
    lidar_top_360fov / lidar_top_360fov.chunk_0000.zip
metadata
    data_collection.parquet
    sensor_presence.parquet

radar
    radar_corner_front_left_srr_0 / radar_corner_front_left_srr_0.chunk_0000.zip
    radar_corner_front_left_srr_3 / radar_corner_front_left_srr_3.chunk_0095.zip
    radar_corner_front_right_srr_0 / radar_corner_front_right_srr_0.chunk_0000.zip
    radar_corner_front_right_srr_3 / radar_corner_front_right_srr_3.chunk_0095.zip
    radar_corner_rear_left_srr_0 / radar_corner_rear_left_srr_0.chunk_0000.zip
    radar_corner_rear_left_srr_3 / radar_corner_rear_left_srr_3.chunk_0095.zip
    radar_corner_rear_right_srr_0 / radar_corner_rear_right_srr_0.chunk_0000.zip
    radar_corner_rear_right_srr_3 / radar_corner_rear_right_srr_3.chunk_0095.zip
    radar_front_center_imaging_lrr_1 / radar_front_center_imaging_lrr_1.chunk_0095.zip
    radar_front_center_mrr_2 / radar_front_center_mrr_2.chunk_0095.zip
    radar_front_center_srr_0 / radar_front_center_srr_0.chunk_0000.zip
    radar_rear_left_mrr_2 / radar_rear_left_mrr_2.chunk_0095.zip
    radar_rear_left_srr_0 / radar_rear_left_srr_0.chunk_0000.zip
    radar_rear_right_mrr_2 / radar_rear_right_mrr_2.chunk_0095.zip
    radar_rear_right_srr_0 / radar_rear_right_srr_0.chunk_0000.zip
    radar_side_left_srr_0 / radar_side_left_srr_0.chunk_0000.zip
    radar_side_left_srr_3 / radar_side_left_srr_3.chunk_0104.zip
    radar_side_right_srr_0 / radar_side_right_srr_0.chunk_0000.zip
    radar_side_right_srr_3 / radar_side_right_srr_3.chunk_0104.zip


    About Data and its FPS, Frequency etc
    -----------------------------------------------



Below is a **single comprehensive technical table** summarizing the **entire dataset structure, statistics, schemas, directories, and annotation usage**.
You can **directly paste this into a README / documentation**.

---

# PhysicalAI Autonomous Vehicles Dataset — Technical Data Overview

| Category               | Component                          | Field / Attribute        | Data Type / Format    | Technical Details                   | Annotation / Usage                          |
| ---------------------- | ---------------------------------- | ------------------------ | --------------------- | ----------------------------------- | ------------------------------------------- |
| Dataset Statistics     | Driving Duration                   | total_hours              | numeric               | 1700 hours of recorded driving data | Dataset scale                               |
| Dataset Statistics     | Clips                              | total_clips              | numeric               | 306,152 clips                       | Each clip is an independent driving segment |
| Dataset Statistics     | Clip Duration                      | clip_duration            | seconds               | 20 seconds                          | Base unit of dataset                        |
| Dataset Statistics     | Camera FPS                         | camera_frame_rate        | numeric               | 30 frames per second                | Frame extraction for annotation             |
| Dataset Statistics     | Frames per Camera per Clip         | frames_per_camera        | numeric               | 600 frames                          | 20 sec × 30 FPS                             |
| Dataset Statistics     | Cameras per Vehicle                | num_cameras              | numeric               | 7 cameras                           | Multi-view perception                       |
| Dataset Statistics     | Frames per Clip (all cameras)      | total_frames_clip        | numeric               | 4200 frames                         | Multi-camera dataset                        |
| Dataset Statistics     | Total Camera Frames                | approx_total_frames      | numeric               | ~1.28 billion frames                | Large-scale visual dataset                  |
| Dataset Statistics     | LiDAR Frequency                    | lidar_frequency          | Hz                    | 10 Hz                               | LiDAR scans per second                      |
| Dataset Statistics     | LiDAR Spins per Clip               | lidar_scans_clip         | numeric               | 200 scans                           | 20 sec × 10 Hz                              |
| Dataset Statistics     | Total LiDAR Scans                  | approx_total_lidar_scans | numeric               | ~61 million scans                   | Large-scale 3D dataset                      |
| Dataset Statistics     | Radar Sensors                      | max_radars               | numeric               | Up to 10 sensors                    | Surround radar detection                    |
| Dataset Statistics     | Dataset Size                       | storage_size             | storage               | ~100 TB                             | Entire dataset storage                      |
| Sensor Modalities      | Camera                             | sensor_type              | video                 | RGB visual capture                  | Primary annotation source                   |
| Sensor Modalities      | LiDAR                              | sensor_type              | point cloud           | 3D spatial sensing                  | 3D object detection                         |
| Sensor Modalities      | Radar                              | sensor_type              | radar detections      | velocity + distance                 | Motion detection                            |
| Sensor Modalities      | Ego Motion                         | sensor_type              | telemetry             | vehicle pose and motion             | trajectory analysis                         |
| Sensor Modalities      | Calibration                        | sensor_type              | parameters            | sensor geometry                     | sensor fusion                               |
| Camera Sensors         | camera_cross_left_120fov           | camera                   | MP4                   | 120° cross left view                | intersection detection                      |
| Camera Sensors         | camera_cross_right_120fov          | camera                   | MP4                   | 120° cross right view               | intersection monitoring                     |
| Camera Sensors         | camera_front_wide_120fov           | camera                   | MP4                   | 120° front wide camera              | lane detection, object detection            |
| Camera Sensors         | camera_front_tele_30fov            | camera                   | MP4                   | 30° telephoto camera                | long-range object detection                 |
| Camera Sensors         | camera_rear_left_70fov             | camera                   | MP4                   | 70° rear left view                  | rear traffic monitoring                     |
| Camera Sensors         | camera_rear_right_70fov            | camera                   | MP4                   | 70° rear right view                 | rear traffic monitoring                     |
| Camera Sensors         | camera_rear_tele_30fov             | camera                   | MP4                   | rear telephoto view                 | distant rear object detection               |
| Camera Data Properties | resolution                         | video_property           | pixels                | 1920 × 1080                         | HD video frames                             |
| Camera Data Properties | format                             | video_format             | MP4                   | H.264 encoded                       | video storage                               |
| Camera Data Properties | fps                                | frame_rate               | numeric               | 30 FPS                              | frame extraction                            |
| Camera Data Properties | frames_clip                        | frames                   | numeric               | 600 frames per camera               | annotation frames                           |
| Camera Directory       | camera/                            | directory                | filesystem            | root camera directory               | camera sensor data                          |
| Camera Directory       | camera_front_wide_120fov           | folder                   | zip chunks            | front wide camera clips             | primary ADAS annotation                     |
| Camera Directory       | camera_cross_left_120fov           | folder                   | zip chunks            | cross left camera clips             | intersection perception                     |
| Camera Directory       | camera_cross_right_120fov          | folder                   | zip chunks            | cross right camera clips            | intersection perception                     |
| Camera Directory       | camera_rear_left_70fov             | folder                   | zip chunks            | rear left camera clips              | rear view detection                         |
| Camera Directory       | camera_rear_right_70fov            | folder                   | zip chunks            | rear right camera clips             | rear view detection                         |
| Camera Directory       | camera_front_tele_30fov            | folder                   | zip chunks            | front tele camera clips             | long distance detection                     |
| Camera Directory       | camera_rear_tele_30fov             | folder                   | zip chunks            | rear tele camera clips              | distant rear detection                      |
| Camera File            | chunk_xxxx.zip                     | compressed               | zip                   | contains ~100 clips                 | dataset distribution                        |
| Camera File            | clip_uuid.camera_xxx.mp4           | video                    | MP4                   | unique clip identifier              | frame extraction                            |
| Camera File            | timestamps.parquet                 | parquet                  | metadata              | frame timestamp data                | multi-sensor sync                           |
| LiDAR Directory        | lidar/                             | directory                | filesystem            | root LiDAR directory                | 3D point cloud data                         |
| LiDAR Directory        | lidar_top_360fov                   | folder                   | zip chunks            | LiDAR sensor data                   | full 360° coverage                          |
| LiDAR File             | clip_uuid.lidar_top360_fov.parquet | parquet                  | LiDAR scan data       | 200 spins per clip                  | 3D annotation                               |
| LiDAR Field            | spin_index                         | int64                    | scan index            | sequential scan number              | LiDAR scan ordering                         |
| LiDAR Field            | reference_timestamp                | int64                    | timestamp             | LiDAR capture time                  | sensor alignment                            |
| LiDAR Field            | draco_encoded_pointcloud           | binary                   | compressed            | Draco encoded point cloud           | 3D reconstruction                           |
| Radar Directory        | radar/                             | directory                | filesystem            | root radar directory                | radar detections                            |
| Radar Directory        | radar_corner_front_left_srr        | folder                   | parquet chunks        | front left radar                    | short-range radar                           |
| Radar Directory        | radar_corner_front_right_srr       | folder                   | parquet chunks        | front right radar                   | short-range radar                           |
| Radar Directory        | radar_side_left_srr                | folder                   | parquet chunks        | left side radar                     | lateral detection                           |
| Radar Directory        | radar_side_right_srr               | folder                   | parquet chunks        | right side radar                    | lateral detection                           |
| Radar Directory        | radar_rear_left                    | folder                   | parquet chunks        | rear radar                          | rear detection                              |
| Radar Directory        | radar_rear_right                   | folder                   | parquet chunks        | rear radar                          | rear detection                              |
| Radar Field            | scan_index                         | int64                    | scan identifier       | radar scan number                   | detection grouping                          |
| Radar Field            | timestamp                          | int64                    | system timestamp      | radar detection time                | synchronization                             |
| Radar Field            | sensor_timestamp                   | int64                    | sensor time           | radar clock timestamp               | synchronization                             |
| Radar Field            | num_returns                        | int64                    | detection count       | radar detections per scan           | object detection                            |
| Radar Field            | azimuth                            | float32                  | horizontal angle      | radar detection angle               | object direction                            |
| Radar Field            | elevation                          | float32                  | vertical angle        | radar detection angle               | object direction                            |
| Radar Field            | distance                           | float32                  | meters                | object distance                     | spatial localization                        |
| Radar Field            | radial_velocity                    | float32                  | m/s                   | relative object velocity            | motion detection                            |
| Radar Field            | rcs                                | float32                  | dBsm                  | radar cross section                 | object reflectivity                         |
| Radar Field            | snr                                | float32                  | dB                    | signal-to-noise ratio               | detection quality                           |
| Radar Field            | exist_probb                        | uint8                    | probability           | object existence probability        | detection confidence                        |
| Calibration            | width                              | int64                    | pixels                | image width                         | camera model                                |
| Calibration            | height                             | int64                    | pixels                | image height                        | camera model                                |
| Calibration            | cx                                 | float64                  | pixels                | principal point X                   | camera intrinsics                           |
| Calibration            | cy                                 | float64                  | pixels                | principal point Y                   | camera intrinsics                           |
| Calibration            | bw_poly_*                          | float64                  | distortion            | backward distortion coefficients    | undistortion                                |
| Calibration            | fw_poly_*                          | float64                  | distortion            | forward distortion coefficients     | projection                                  |
| Sensor Extrinsics      | qx qy qz qw                        | float64                  | quaternion            | sensor orientation                  | coordinate transform                        |
| Sensor Extrinsics      | x y z                              | float64                  | meters                | sensor position                     | sensor alignment                            |
| Coordinate System      | origin                             | location                 | vehicle frame         | center of rear axle                 | spatial reference                           |
| Coordinate System      | X axis                             | direction                | forward               | vehicle heading                     | navigation                                  |
| Coordinate System      | Y axis                             | direction                | left                  | lateral direction                   | navigation                                  |
| Coordinate System      | Z axis                             | direction                | up                    | vertical axis                       | navigation                                  |
| Vehicle Dimensions     | length                             | float64                  | meters                | vehicle length                      | bounding box validation                     |
| Vehicle Dimensions     | width                              | float64                  | meters                | vehicle width                       | geometry validation                         |
| Vehicle Dimensions     | height                             | float64                  | meters                | vehicle height                      | geometry validation                         |
| Vehicle Dimensions     | wheelbase                          | float64                  | meters                | axle distance                       | vehicle dynamics                            |
| Vehicle Dimensions     | track_width                        | float64                  | meters                | wheel separation                    | vehicle geometry                            |
| Ego Motion             | timestamp                          | int64                    | time                  | vehicle state timestamp             | temporal alignment                          |
| Ego Motion             | qx qy qz qw                        | float64                  | quaternion            | vehicle orientation                 | trajectory                                  |
| Ego Motion             | x y z                              | float64                  | meters                | vehicle position                    | mapping                                     |
| Ego Motion             | vx vy vz                           | float64                  | m/s                   | vehicle velocity                    | motion analysis                             |
| Ego Motion             | ax ay az                           | float64                  | m/s²                  | vehicle acceleration                | dynamics                                    |
| Ego Motion             | curvature                          | float64                  | 1/m                   | trajectory curvature                | path estimation                             |
| Sensor Presence        | camera_*                           | bool                     | availability          | indicates camera presence           | dataset filtering                           |
| Sensor Presence        | lidar_top_360fov                   | bool                     | availability          | LiDAR present or not                | dataset filtering                           |
| Sensor Presence        | radar_*                            | bool                     | availability          | radar presence flags                | dataset filtering                           |
| Radar Config           | radar_config                       | string                   | NA / low / med / high | radar configuration level           | sensor setup                                |
| Data Collection        | clip_id                            | string                   | UUID                  | unique clip identifier              | cross-sensor mapping                        |
| Data Collection        | country                            | string                   | geographic metadata   | recording country                   | geographic analysis                         |
| Data Collection        | month                              | int64                    | temporal metadata     | recording month                     | seasonal analysis                           |
| Data Collection        | hour_of_day                        | int64                    | temporal metadata     | time of recording                   | day/night filtering                         |
| Data Collection        | platform_class                     | string                   | vehicle platform      | hyperion_8 / hyperion_8.1           | platform reference                          |
| Annotation Usage       | Camera Frames                      | visual data              | RGB frames            | 2D perception                       | bounding boxes                              |
| Annotation Usage       | Camera Frames                      | visual data              | RGB frames            | semantic understanding              | segmentation                                |
| Annotation Usage       | Camera Frames                      | visual data              | RGB frames            | road understanding                  | lane marking                                |
| Annotation Usage       | Camera Frames                      | visual data              | RGB frames            | traffic infrastructure              | traffic signs                               |
| Annotation Usage       | LiDAR Point Cloud                  | 3D data                  | spatial geometry      | object localization                 | 3D bounding boxes                           |
| Annotation Usage       | Radar Data                         | radar detection          | velocity sensing      | moving objects                      | object tracking                             |
| Annotation Usage       | Multi Sensor                       | fused data               | sensor fusion         | perception stack                    | ADAS model training                         |
