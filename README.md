# A-comparative-study-on-point-cloud-down-sampling-strategies-for-deep-learning-based-crop-organ-segmentation
This repo contains the official codes for our paper:

### **A comparative study on point cloud down-sampling strategies for deep learning-based crop organ segmentation**

[Dawei Li](https://davidleepp.github.io/),  [Yongchang Wei](https://github.com/WeiyongchangChina), and Rongsheng Zhu

Published on *Plant Methods* in 2023

[[Paper](https://link.springer.com/article/10.1186/s13007-023-01099-7)]

___

## Prerequisites

- Python == 3.7.13
- Numpy == 1.21.5
- tensorflow == 1.13.1
- CUDA == 11.7
- cuDNN == 10.1
- PCL == 1.120

## Abstract

The 3D crop data obtained during cultivation is of great signifcance to screening excellent varieties in modern breeding and improvement on crop yield. With the rapid development of deep learning, researchers have been making  innovations in aspects of both data preparation and deep network design for segmenting plant organs from 3D  data. 

Training of the deep learning network requires the input point cloud to have a fxed scale, which means all  point clouds in the batch should have similar scale and contain the same number of points. A good down-sampling  strategy can reduce the impact of noise and meanwhile preserve the most important 3D spatial structures. As far  as we know, this work is the frst comprehensive study of the relationship between multiple down-sampling strategies and the performances of popular networks for plant point clouds. 

Five down-sampling strategies (including  FPS, RS, UVS, VFPS, and 3DEPS) are cross evaluated on fve diferent segmentation networks (including PointNet+ +,  DGCNN, PlantNet, ASIS, and PSegNet). The overall experimental results show that currently there is no strict golden  rule on fxing down-sampling strategy for a specifc mainstream crop deep learning network, and the optimal downsampling strategy may vary on diferent networks. However, some general experience for choosing an appropriate  sampling method for a specifc network can still be summarized from the qualitative and quantitative experiments. 

 First, 3DEPS and UVS are easy to generate better results on semantic segmentation networks. Second, the voxel-based  down-sampling strategies may be more suitable for complex dual-function networks. Third, at 4096-point resolution,  3DEPS usually has only a small margin compared with the best down-sampling strategy at most cases, which means  3DEPS may be the most stable strategy across all compared. This study not only helps to further improve the accuracy  of point cloud deep learning networks for crop organ segmentation, but also gives clue to the alignment of downsampling strategies and a specifc network

![](docs/down-sampling&network.png)

## File Structure

```
Abstract  
├─data-example  
│  ├─3DEPS_ratio=0.20  
│  └─raw-data  
├─deep-learning-network  
│  ├─ASIS  
│  │  ├─data  
│  │  ├─models  
│  │  ├─log  
│  │  │  ├─test  
│  │  │  └─train  
│  │  ├─tf_ops  
│  │  │  ├─3d_interpolation  
│  │  │  ├─grouping  
│  │  │  └─sampling  
│  │  └─utils  
│  ├─DGCNN  
│  │  ├─data  
│  │  ├─models  
│  │  ├─part_seg  
│  │  │  ├─log  
│  │  │  │  ├─test  
│  │  │  │  └─train  
│  │  ├─tf_ops  
│  │  │  ├─3d_interpolation  
│  │  │  ├─grouping  
│  │  │  │  ├─test  
│  │  │  └─sampling  
│  │  └─utils  
│  ├─PlantNet  
│  │  ├─data  
│  │  ├─models  
│  │  │  ├─log_test  
│  │  │  │  ├─test  
│  │  │  │  └─train  
│  │  ├─tf_ops  
│  │  │  ├─3d_interpolation  
│  │  │  ├─grouping  
│  │  │  │  ├─test  
│  │  │  └─sampling  
│  │  └─utils  
│  ├─PointNet++  
│  │  ├─data  
│  │  ├─models  
│  │  ├─part_seg  
│  │  ├─tf_ops  
│  │  │  ├─3d_interpolation  
│  │  │  ├─grouping  
│  │  │  │  ├─test  
│  │  │  └─sampling  
│  │  └─utils  
│  └─PSegNet  
│      ├─data  
│      ├─models  
│      │  ├─log_test  
│      │  │  ├─test  
│      │  │  └─train  
│      ├─tf_ops  
│      │  ├─3d_interpolation  
│      │  ├─grouping  
│      │  │  ├─test  
│      │  └─sampling  
│      └─utils  
├─docs  
└─down-sampling-strategies  
    ├─3DEPS  
    ├─dataset-creation-process  
    ├─FPS  
    ├─RS  
    ├─UVS  
    └─VFPS   
```

## Down-Sampling Code 

The downsampling strategy in the open source code is saved in folder [down-sampling-strategies].

They are FPS, 3DEPS, RS, VFPS, UVS respectively.

### 1. FPS

FPS(Farthest Point Sampling) is a commonly used downsampling strategy.

- The `FPS_Batch.py` is the entry codes for point set down-sampling.

### 2. 3DEPS

3DEPS(3D Edge‑Preserving Sampling) is a downsampling strategy based on human sketching ideas.[[Paper](https://www.sciencedirect.com/science/article/pii/S0924271622000119)]

- The `001批量保存植物边缘和中心部位(c++).cpp` is used to save plant edges and center points in batches respectively.
- The `002将边缘部分和非边缘部分合并到4096+4096.py` is to merge the edge part and the non-edge part into 4096+4096.
- The `003按比例合并成一个新点云同时进行10倍扩充.py` merged into a new point cloud in proportion and expanded 10 times at the same time.

**Notice! Programs need to be run one by one in order of name and number.**

**001 needs to be run using PCL (Point Cloud Library).**

### 3. RS

RS(Random sampling) is a sequential random sampling strategy using functions from the PCL library.

- The `RandomSample.cpp` is the entry codes for point set down-sampling.

### 4. VFPS

VFPS(Voxelized Farthest  Point Sampling) is a voxel downsampling strategy. Used in PSegnet.[[Paper](https://spj.science.org/doi/full/10.34133/2022/9787643?adobe_mc=MCMID%3D14000805405683999525849378418609464876%7CMCORGID%3D242B6472541199F70A4C98A6%2540AdobeOrg%7CTS%3D1700524800)]

- The `001Voxel_filter.cpp` is to voxel downsample the point cloud.
- The `002FPS_Batch.py` is fps downsampling, which fixes the number of points in the point cloud after voxelization downsampling and expands it.

**Notice! Programs need to be run one by one in order of name and number.**

**001 needs to be run using PCL (Point Cloud Library).**

### 5. UVS

UVS(Uniform Voxel  Sampling) is a voxel downsampling strategy.

- The `001uniformSampling.cpp` is the entry codes for point set down-sampling.
- The `002FPS_Batch.py` is fps downsampling, which fixes the number of points in the point cloud after voxelization downsampling and expands it.

**Notice! Programs need to be run one by one in order of name and number.**

**001 needs to be run using PCL (Point Cloud Library).**

### 6. dataset-creation-process

All the above codes are not the complete downsampling process. In the  [down-sampling-strategies/dataset-creation-process] folder is the complete process of downsampling processing.

- The `000批量修改label格式(python).py` is used to modify label formats in batches
- The `001PCD2TXT(python).py` is used to convert files from PCD to txt format, which can be skipped according to specific needs.
- The `002去除背景点和噪点.py` is used to remove background points and noise in the original point cloud.
- The `003去除在原点的点.py` is used to remove points at the origin.
- The `004添加object标签类别减2.py` is used to remove the labels of background points and noise points.
- The `005各种降采样策略.txt` is to use the above five downsampling strategies to replace 005.
- The `006分测试集和训练集.py` is used to divide the expanded point cloud into a training set and a test set.
- The `007将txt转换成H5(python).py` is used to convert txt point cloud into h5 file.

**Notice! Programs need to be run one by one in order of name and number.**

## Point Clouds Networks

The Point Clouds Networks in the open source code is saved in folder [deep-learning-network].

They are ASIS, DGCNN, PlantNet, PSegNet, PointNet++ respectively.

We deliberately save a trained model in the log file in the project file of each network for testing only.

The dataset for each network is saved in the data folder.

## data sample

We saved an example dataset in the [data-example] folder.

It contains a prepared h5 data set using 3DEPS_ratio=0.20, which is divided into a training set and a test set. and an original three-species crop data set.
