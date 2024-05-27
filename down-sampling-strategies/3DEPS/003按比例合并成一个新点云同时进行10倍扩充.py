"""
Created on Sat Oct  9 12:35:05 2022

@author: YC-W
"""

import numpy as np
import os
import torch
from os import listdir, path

#@numba.jit()
def get_filelist(path):
    Filelist = []
    for home, dirs, files in os.walk(path):
        for filename in files:
             Filelist.append(os.path.join(home, filename))
    return Filelist

def get_files(path):
    for home, dirs, files in os.walk(path):
        return files


def farthest_point_sample(xyz, npoint, z):
    device = xyz.device
    N, C = xyz.shape
    torch.manual_seed(z)
    centroids = torch.zeros(npoint, dtype=torch.long).to(device)
    distance = torch.ones(N, dtype=torch.float64).to(device) * 1e10
    farthest = torch.randint(0, N, (1,),dtype=torch.long).to(device)
    for i in range(npoint):
        centroids[i] = farthest
        centroid = xyz[farthest, :].view(1, 3)
        dist = torch.sum((xyz - centroid) ** 2, -1)
        mask = dist < distance
        distance[mask] = dist[mask]
        farthest = torch.max(distance, -1)[1]
    return centroids


if __name__ == '__main__':
    path = r'D:\cpp_project\PCL1\downsampling_ex\3DEPS\data_edge&core\合并'  # 注意，此处路径不要有中文
    Filelist = get_filelist(path)
    FILES = get_files(path=r'D:\cpp_project\PCL1\downsampling_ex\3DEPS\data_edge&core\合并')

    for z in range(0, 9):
        i = 0
        for file in Filelist:
            # ply = o3d.io.read_point_cloud(file)
            # points = np.loadtxt(file,dtype=float,delimiter=',')
            points = np.loadtxt(file)
            # points=data_f[10:]
            pcd_array = np.asarray(points)
            print(file, pcd_array.shape)
            sample_count = 4096  # 固定FPS降采样后的点数
            ratio = 0.2
            b = torch.from_numpy(pcd_array)
            b = b[:, : 3]
            edg_points_index = farthest_point_sample(b[0:4096], sample_count - int(sample_count * ratio), z)
            center_points_index = farthest_point_sample(b[4096:8192], int(sample_count * ratio), z)
            for j in range(int(sample_count * ratio)):
                edg_points_index[j] = edg_points_index[j] + 4096
            sampled_points_index = np.concatenate((center_points_index, edg_points_index), axis=0)
            sample_point = np.zeros((4096, 5))
            for j in range(4096):
                sample_point[j] = pcd_array[sampled_points_index[j]]
            # np.savetxt("id//"+file[0:len(file)- 3]+"txt",sampled_points_index)
            # np.savetxt(file[0:len(file)- 3]+"txt",sampled_points_index)
            np.savetxt(r'D:\cpp_project\PCL1\temp\data\end\\' + str(FILES[i]) + str(z)  + ".txt", sample_point, fmt="%f %f %f %d %d")  # J仅仅是使保存的文件不重名而已
            i = i + 1