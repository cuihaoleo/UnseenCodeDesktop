#!/usr/bin/env python3

import numpy as np
import argparse
import cv2
import sys
import os

def gen_color_ct(trans):
    inv_trans = np.linalg.inv(trans)

    min_ct = np.zeros((3, 3), dtype=float)
    min_ct[:, :2] = -inv_trans[:, (0, 2)] / inv_trans[:, (1, )]
    max_ct = min_ct.copy()
    for i in range(3):
        if inv_trans[i, 1] > 0:
            max_ct[i, 2] = 1.0 / inv_trans[i, 1]
        else:
            min_ct[i, 2] = 1.0 / inv_trans[i, 1]
    return min_ct, max_ct


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source image")
    parser.add_argument("mask", help="Mask image")
    parser.add_argument("--scale", type=float, default=0.95, help="Scale factor")
    parser.add_argument("--matrix", default="matrix.in", help="Transform matrix")
    parser.add_argument("--out1", default="out1.png", help="Output 1")
    parser.add_argument("--out2", default="out2.png", help="Output 2")
    args = parser.parse_args()

    assert 0 <= args.scale <= 1
    assert os.path.isfile(args.source)
    assert os.path.isfile(args.mask)

    trans = np.loadtxt(args.matrix)
    inv_trans = np.linalg.inv(trans)

    img = cv2.imread(args.source, cv2.IMREAD_COLOR)
    msk = cv2.imread(args.mask, cv2.IMREAD_GRAYSCALE)
    msk = cv2.resize(msk, img.shape[1::-1], interpolation=cv2.INTER_NEAREST)
    height, width = msk.shape

    img_f32 = img / 255.0
    msk_seq = msk.flatten().astype(np.bool)
    bgr_seq = img_f32.reshape((-1, 3))
    ycc_seq = bgr_seq @ trans.T

    min_ct, max_ct = gen_color_ct(trans)
    ycc1_seq = ycc_seq.copy()
    ycc1_seq[:, 1] = ycc1_seq[:, 2]
    ycc1_seq[:, 2] = 1
    ca_min = (ycc1_seq @ min_ct.T).max(axis=1)
    ca_max = (ycc1_seq @ max_ct.T).min(axis=1)

    d_ca = np.minimum(ycc_seq[:, 1] - ca_min, ca_max - ycc_seq[:, 1])
    np.clip(d_ca, 0, None, out=d_ca)
    d_ca_limit = d_ca.max() * args.scale
    #d_ca *= args.scale
    print(d_ca.max())
    np.clip(d_ca, 0.0, d_ca_limit, out=d_ca)

    # modify Ca channel
    ycc_seq_i1 = ycc_seq.copy()
    ycc_seq_i1[msk_seq, 1] += d_ca[msk_seq]
    ycc_seq_i1[~msk_seq, 1] -= d_ca[~msk_seq]
    bgr_seq_i1 = ycc_seq_i1 @ inv_trans.T
    bgr_i1 = bgr_seq_i1.reshape((height, width, -1))
    bgr_i2 = 2 * img_f32 - bgr_i1

    assert np.all(bgr_i1 >= -0.001)
    assert np.all(bgr_i1 < 1.001)
    assert np.all(bgr_i2 >= -0.001)
    assert np.all(bgr_i2 < 1.001)
    np.clip(bgr_i1, 0.0, 1.0, out=bgr_i1)
    np.clip(bgr_i2, 0.0, 1.0, out=bgr_i2)
    i1 = np.uint8(np.round(bgr_i1 * 255))
    i2 = np.uint8(np.round(bgr_i2 * 255))

    cv2.imwrite(args.out1, i1)
    cv2.imwrite(args.out2, i2)


if __name__ == "__main__":
    main()
