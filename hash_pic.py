import itertools
import os
from glob import glob
from pprint import pprint

import numpy as np
from PIL import Image

from feature_fusion.VLAD import VLAD
from descriptors.HardNetDescriptor import HardNetDescriptor
from termcolor import colored
from tqdm import tqdm
from lshash import LSHash


class PQTable:
    def __init__(self):
        pass

    def fit(self, hash_list: list):
        pass

    def find(self, hash_str: str, threshold: float, metric: str):
        pass

    def dump(self):
        pass


def compute_feature_vector(pic: Image, feature_descriptor, feature_detect_method=None, fusion_method=None):
    """
    提取图片特征向量
    :param pic:     当前需要进行特征向量提取的图片
    :param feature_descriptor:    特征描述函数
    :param feature_detect_method:   特征点检测函数，如果为None，则将整张图片作为特征点
    :param fusion_method:       特征融合函数，如果为None，则就输出图片的特征，不需要融合
    :return:    n*m，n为特征点数，m为每个特征向量长度
    """
    pic_patches = feature_detect_method(pic) if feature_detect_method is not None else \
        [np.array(pic.convert('L').resize((32, 32))), ]
    feature_vectors = feature_descriptor(pic_patches)
    assert feature_vectors is not None, '特征向量不能为空'
    to_return = fusion_method(feature_vectors) if fusion_method is not None else feature_vectors
    if len(to_return) == 1:
        to_return = to_return[0]
    assert len(to_return.shape) == 1, '需要进行特征融合变为一个特征向量'
    return to_return


def get_item_pic_train_dataset(pic_folder, desc):
    all_train_item_pic = [[np.array(Image.open(m_file).convert('L').resize((32, 32))), ] for m_file in
                          glob(os.path.join(pic_folder, '*_[0-9].jpg'))]
    return np.array(list(itertools.chain.from_iterable(
        [desc.describle(m_train_item_pic) for m_train_item_pic in all_train_item_pic])))


def get_word_pic_train_dataset(pic_folder, desc):
    all_train_word_pic = [[np.array(Image.open(m_file).convert('L').resize((32, 32))), ] for m_file in
                          glob(os.path.join(pic_folder, '*_desc.jpg'))]
    return np.array(list(itertools.chain.from_iterable(
        [desc.describle(m_train_word_pic) for m_train_word_pic in all_train_word_pic])))


def word_pic_tps(pic: Image):
    # 对文字图像进行tps
    return pic


def hash_word_pic(pic_folder):
    # 对图像进行stn-tps形变
    all_pics = []
    all_feature_vector = []
    for m_pic in all_pics:
        transformed_word_pic = word_pic_tps(m_pic)
        # 计算图像的surf特征
        all_feature_vector.append(compute_feature_vector(transformed_word_pic, 'surf'))
    # 配置LSH
    # word_pic_lsh = LSH()
    # word_pic_lsh.fit(all_feature_vector)

    # for m_feature_vector in all_feature_vector:
    #     # 输出每张图的hash字符串到文件
    #     yield word_pic_lsh.transform(m_feature_vector)
    # word_pic_lsh.dump(os.path.join('.','word_pic_lsh.pkl'))


def hash_item_pic_v1(pic_folder):
    """
    当前版本采用HardNet直接进行特征输出，并且对整张图作为特征区域进行特征向量输出，会在图片所在同级
    目录输出一个图片与hash值编码的映射文件

    这种方案出来的结果是如果图片有平移则特征向量会有差距

    :param pic_folder:  所有图片所在文件夹
    :return:    是否成功
    """
    try:
        # 计算所有图片的特征向量
        desc = HardNetDescriptor()
        print(colored("HardNet模型加载完成", color='blue'))
        # 使用LSH
        lsh = LSHash(16, 128)
        img_feature_vector = {}
        with open(pic_folder + '_item_hash.txt', 'w') as to_write:
            img_file_list = glob(os.path.join(pic_folder, '*_[0-9].jpg'))
            for m_img_file in tqdm(img_file_list,desc='训练中'):
                fv = desc.describle([np.array(Image.open(m_img_file).convert('L').resize((32, 32))), ])[0]
                img_feature_vector[m_img_file] = fv
                lsh.index(fv,extra_data=m_img_file)
            for m_img_file in tqdm(img_file_list,desc='输出中'):
                res = lsh.query(img_feature_vector[m_img_file],distance_func='centred_euclidean')
                # 输出所有临近的图片
                print(m_img_file,'|'.join(map(lambda x:x[0][1],res)))
        pass
        return True
    except Exception as e:
        print(colored("错误:%s" % str(e), color='red'))
        return False




def load_to_pqtable():
    # 加载当前所有数据加载至pqtable中，并保存为文件
    pass


if __name__ == '__main__':
    #
    # descriptor = HardNetDescriptor()
    # test_pic_folder = "../12306/12306_pics_test_cut"
    # # item_train_dataset = get_item_pic_train_dataset(test_pic_folder,descriptor)
    # vlad = VLAD(exist_visual_dict='./item_test_kmeans_cluster.pkl')
    # # vlad.train(item_train_dataset,'./item_test_kmeans_cluster.pkl')
    # pic_path = "../12306/12306_pics_test_cut/0a0a88f7-2f20-11e9-91b7-b4b686ea7832_2.jpg"
    # pic = Image.open(pic_path)
    # np.set_printoptions(threshold=np.inf)
    # print(compute_feature_vector(pic, descriptor.describle, fusion_method=vlad.aggregate))

    hash_item_pic_v1('../12306/12306_pics_test_cut')