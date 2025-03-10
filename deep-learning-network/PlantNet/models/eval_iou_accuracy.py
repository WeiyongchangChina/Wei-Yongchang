import os
import numpy as np
from scipy import stats

NUM_CLASSES = 6
MAX_POINTS = 4096

pred_data_label_filenames = []
file_name = '/media/dawei-server/DATA - SSD1TB/wyc/服务器训练/data_sgl/data_net_sgl/PlantNet_temp2/models/out/output_filelist.txt'
pred_data_label_filenames += [line.rstrip() for line in open(file_name)]

gt_label_filenames = [f.rstrip('pred.txt') + 'gt.txt' for f in pred_data_label_filenames]

num_room = len(gt_label_filenames)

# Initialize...
# acc and macc
total_true = 0
total_seen = 0
true_positive_classes = np.zeros(NUM_CLASSES)
true_negative_classes = np.zeros(NUM_CLASSES)
false_positive_classes = np.zeros(NUM_CLASSES)
false_negative_classes = np.zeros(NUM_CLASSES)
positive_classes = np.zeros(NUM_CLASSES)
gt_classes = np.zeros(NUM_CLASSES)
# mIoU
ious = np.zeros(NUM_CLASSES)
totalnums = np.zeros(NUM_CLASSES)
# precision & recall
total_gt_ins = np.zeros(NUM_CLASSES)
at = 0.5
tpsins = [[] for itmp in range(NUM_CLASSES)]
fpsins = [[] for itmp in range(NUM_CLASSES)]
# mucov and mwcov
all_mean_cov = [[] for itmp in range(NUM_CLASSES)]
all_mean_weighted_cov = [[] for itmp in range(NUM_CLASSES)]

data_label = []
gt_label = []
for i in range(len(pred_data_label_filenames)):
    print('load file %d...'%i)
    current_data_label = np.loadtxt(pred_data_label_filenames[i])
    current_gt_label = np.loadtxt(gt_label_filenames[i])
    data_label.append(current_data_label)
    gt_label.append(current_gt_label)
data_label = np.concatenate(data_label, axis=0)
gt_label = np.concatenate(gt_label, axis=0)
    
# # change plant-2 stem gt label from 0 to 4 and plant-3 stem gt label from 0 to 5
# find_index1 = list(np.where(gt_label[:,0]==0)[0])
# find_index2 = list(np.where(gt_label[:,2]!=0)[0])
# find_index_gt = list(set(find_index1).intersection(set(find_index2)))
# gt_label[find_index_gt,0] = gt_label[find_index_gt,2] + 3 # gt_sem gt_ins gt_obj
# # change pred label
# find_index3 = list(np.where(data_label[:,4]==0)[0])
# find_index_pre = list(set(find_index2).intersection(set(find_index3)))
# data_label[find_index_pre,4] = gt_label[find_index_pre,2] + 3 # X Y Z pro pre_sem pre_ins

# # according obj label to refine one plant just have one type leaf
# # for plant one
# plant_1_pre_index = list(np.where(data_label[:,4]>0)[0])
# plant_1_obj_index = list(np.where(gt_label[:,2]==0)[0])
# plant_1_index = list(set(plant_1_pre_index).intersection(set(plant_1_obj_index)))
# data_label[plant_1_index,4] = 1
# # for plant two
# plant_2_pre_index = list(np.where(data_label[:,4]!=4)[0])
# plant_2_obj_index = list(np.where(gt_label[:,2]==1)[0])
# plant_2_index = list(set(plant_2_pre_index).intersection(set(plant_2_obj_index)))
# data_label[plant_2_index,4] = 2
# # for plant three
# plant_3_pre_index = list(np.where(data_label[:,4]!=5)[0])
# plant_3_obj_index = list(np.where(gt_label[:,2]==2)[0])
# plant_3_index = list(set(plant_3_pre_index).intersection(set(plant_3_obj_index)))
# data_label[plant_3_index,4] = 3

plant_number = data_label.shape[0]//MAX_POINTS

for i in range(plant_number):
    print('%d / %d ...' % (i, plant_number))
#    print(i)
    start_index = i * MAX_POINTS
    end_index = (i+1) * MAX_POINTS
    pred_ins = data_label[start_index:end_index,-1].reshape(-1).astype(np.int)
    pred_sem = data_label[start_index:end_index, -2].reshape(-1).astype(np.int)
#    pred_sem[pred_sem != 5] = 1
#    pred_sem[pred_sem == 5] = 0
    gt_ins = gt_label[start_index:end_index, 1].reshape(-1).astype(np.int)
    gt_sem = gt_label[start_index:end_index, 0].reshape(-1).astype(np.int)
#    gt_sem[gt_sem != 5] = 1
#    gt_sem[gt_sem == 5] = 0
    gt_obj = gt_label[start_index:end_index, 2].reshape(-1).astype(np.int)

    # pn semantic mIoU
    for j in range(gt_sem.shape[0]):
        gt_l = int(gt_sem[j])
        pred_l = int(pred_sem[j])
        gt_classes[gt_l] += 1
        positive_classes[pred_l] += 1
        true_positive_classes[pred_l] += int(gt_l==pred_l)
        false_positive_classes[pred_l] += int(gt_l!=pred_l)
        false_negative_classes[gt_l] += int(gt_l!=pred_l)
 
    # instance
    un = np.unique(pred_ins)
    pts_in_pred = [[] for itmp in range(NUM_CLASSES)]
    for ig, g in enumerate(un):  # each object in prediction
        if g == -1:
            continue
        tmp = (pred_ins == g)
        sem_seg_i = int(stats.mode(pred_sem[tmp])[0])
        pts_in_pred[sem_seg_i] += [tmp]

    un = np.unique(gt_ins)
    pts_in_gt = [[] for itmp in range(NUM_CLASSES)]
    for ig, g in enumerate(un):
        tmp = (gt_ins == g)
        sem_seg_i = int(stats.mode(gt_sem[tmp])[0])
        pts_in_gt[sem_seg_i] += [tmp]

    # instance mucov & mwcov
    for i_sem in range(NUM_CLASSES):
        sum_cov = 0
        mean_cov = 0
        mean_weighted_cov = 0
        num_gt_point = 0
        for ig, ins_gt in enumerate(pts_in_gt[i_sem]):
            ovmax = 0.
            num_ins_gt_point = np.sum(ins_gt)
            num_gt_point += num_ins_gt_point
            for ip, ins_pred in enumerate(pts_in_pred[i_sem]):
                union = (ins_pred | ins_gt) # or
                intersect = (ins_pred & ins_gt) # and
                iou = float(np.sum(intersect)) / np.sum(union)

                if iou > ovmax:
                    ovmax = iou
                    ipmax = ip

            sum_cov += ovmax
            mean_weighted_cov += ovmax * num_ins_gt_point

        if len(pts_in_gt[i_sem]) != 0:
            mean_cov = sum_cov / len(pts_in_gt[i_sem])
            all_mean_cov[i_sem].append(mean_cov)

            mean_weighted_cov /= num_gt_point
            all_mean_weighted_cov[i_sem].append(mean_weighted_cov)
            
            
    # instance precision & recall
    for i_sem in range(NUM_CLASSES):
        tp = [0.] * len(pts_in_pred[i_sem])
        fp = [0.] * len(pts_in_pred[i_sem])
        gtflag = np.zeros(len(pts_in_gt[i_sem]))
        total_gt_ins[i_sem] += len(pts_in_gt[i_sem])

        for ip, ins_pred in enumerate(pts_in_pred[i_sem]):
            ovmax = -1.

            for ig, ins_gt in enumerate(pts_in_gt[i_sem]):
                union = (ins_pred | ins_gt)
                intersect = (ins_pred & ins_gt)
                iou = float(np.sum(intersect)) / np.sum(union)

                if iou > ovmax:
                    ovmax = iou
                    igmax = ig

            if ovmax >= at:
                    tp[ip] = 1  # true
            else:
                fp[ip] = 1  # false positive

        tpsins[i_sem] += tp
        fpsins[i_sem] += fp


MUCov = np.zeros(NUM_CLASSES)
MWCov = np.zeros(NUM_CLASSES)
for i_sem in range(NUM_CLASSES):
    MUCov[i_sem] = np.mean(all_mean_cov[i_sem])
    MWCov[i_sem] = np.mean(all_mean_weighted_cov[i_sem])

precision = np.zeros(NUM_CLASSES)
recall = np.zeros(NUM_CLASSES)
for i_sem in range(NUM_CLASSES):
    tp = np.asarray(tpsins[i_sem]).astype(np.float)
    fp = np.asarray(fpsins[i_sem]).astype(np.float)
    tp = np.sum(tp)
    fp = np.sum(fp)
    rec = tp / total_gt_ins[i_sem]
    prec = tp / (tp + fp)

    precision[i_sem] = prec
    recall[i_sem] = rec


LOG_FOUT = open(os.path.join('log_6_BS74_0.3.txt'), 'w')
def log_string(out_str):
    LOG_FOUT.write(out_str+'\n')
    LOG_FOUT.flush()
    print(out_str)


# instance results
log_string('Instance Segmentation Cov: {}'.format(MUCov))
#log_string('Instance Segmentation mMUCov: {}'.format(np.mean(MUCov)))
log_string('Instance Segmentation WCov: {}'.format(MWCov))
#log_string('Instance Segmentation mMWCov: {}'.format(np.mean(MWCov)))
log_string('Instance Segmentation Precision: {}'.format(precision))
#log_string('Instance Segmentation mPrecision: {}'.format(np.mean(precision)))
log_string('Instance Segmentation Recall: {}'.format(recall))
#log_string('Instance Segmentation mRecall: {}'.format(np.mean(recall)))

# semantic results
iou_list = []
for i in range(NUM_CLASSES):
    iou = true_positive_classes[i]/float(gt_classes[i]+positive_classes[i]-true_positive_classes[i]) 
    iou_list.append(iou)

precision = true_positive_classes / (false_positive_classes+true_positive_classes)
recall = true_positive_classes / (false_negative_classes+true_positive_classes)

log_string('Semantic Segmentation Precision: {}'.format(precision))
log_string('Semantic Segmentation Recall: {}'.format(recall))
log_string('Semantic Segmentation F1-score: {}'.format(2*precision*recall/(precision+recall)))
#log_string('Semantic Segmentation oAcc: {}'.format(true_positive_classes/positive_classes))
#log_string('Semantic Segmentation Acc: {}'.format(true_positive_classes / gt_classes))
#log_string('Semantic Segmentation mAcc: {}'.format(np.mean(true_positive_classes / gt_classes)))
log_string('Semantic Segmentation IoU: {}'.format( np.array(iou_list)))
#log_string('Semantic Segmentation mIoU: {}'.format(1.*sum(iou_list)/NUM_CLASSES))
