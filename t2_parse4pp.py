#!/usr/bin/env python3

import sys
import argparse
import numpy as np
import cv2
from scipy.linalg import hadamard
import matplotlib.pyplot as plt
from s2_gen_mask import get_base

DEST_WIDTH = 1200

def normal_save(path, m):
    img = m - m.min()
    img /= img.max()
    img = np.uint8(img * 255.0)
    cv2.imwrite(path, img)

def decode(ca, cb, n_block):
    assert ca.shape == cb.shape
    assert ca.shape[0] == ca.shape[1]
    dest_width = ca.shape[0]
    patch_width = dest_width // n_block

    step1 = np.linspace(0, dest_width, n_block, False, dtype=int)
    step2 = np.linspace(0, dest_width, 2*n_block, False, dtype=int)[1:-1:2]
    hada = hadamard(8)
    mat, _, _ = get_base(patch_width)
    msg = []
    count = 0

    for step in (step1, step2):
        for sy in step:
            for sx in step:
                pca = ca[sy:sy+patch_width, sx:sx+patch_width]
                pcb = cb[sy:sy+patch_width, sx:sx+patch_width]

                pca = cv2.normalize(pca - pca.mean(), None, alpha=1.0, norm_type=cv2.NORM_L2)
                pcb = cv2.normalize(pcb - pcb.mean(), None, alpha=1.0, norm_type=cv2.NORM_L2)
                #pc1 -= pc1.mean()
                #pc1 /= pc1.std()
                #pc2 -= pc2.mean()
                #pc2 /= pc2.std()

                b8ca = cv2.warpAffine(pca, mat, (8, 8),
                                      flags=cv2.WARP_INVERSE_MAP)
                b8cb = cv2.warpAffine(pcb, mat, (8, 8),
                                      flags=cv2.WARP_INVERSE_MAP)

                diff = b8ca - b8cb
                dht = np.abs(hada @ diff @ hada)

                if dht[2, 0] + dht[3, 0] > dht[0, 2] + dht[0, 3]:
                    bit = 1
                else:
                    bit = 0

                msg.append(bit)
                count += 1

    msg = np.array(msg)
    bitmap = msg[:-1].reshape(2*(n_block-1), n_block)
    return bitmap


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", nargs="+", help="Target images")
    parser.add_argument("--matrix", default="matrix.in", help="Transform matrix")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ref", help="Compare result to the bitmap")
    group.add_argument("--block", type=int, help="N blocks")

    args = parser.parse_args()

    if args.ref is not None:
        ref_bitmap = cv2.imread(args.ref, cv2.IMREAD_GRAYSCALE) // 255
        n_block = ref_bitmap.shape[1]
    else:
        ref_bitmap = None
        n_block = args.block

    trans = np.loadtxt(args.matrix)
    bitmap_sum = np.zeros((2*(n_block-1), n_block), dtype=int)
    for cap_path in args.targets:
        cap = cv2.imread(cap_path, cv2.IMREAD_COLOR) / 255.0
        resized = cv2.resize(cap, (DEST_WIDTH, DEST_WIDTH))
        #resized = cv2.resize(cap, (DEST_WIDTH, DEST_WIDTH), interpolation=cv2.INTER_AREA)
        resized = cv2.GaussianBlur(resized, (9, 9), 0, 0)

        bgr_seq = resized.reshape((-1, 3))
        ycc_seq = bgr_seq @ trans.T
        ycc = ycc_seq.reshape(resized.shape)

        yu = ycc[:, :, 0]
        ca = ycc[:, :, 1]
        cb = ycc[:, :, 2]
        #normal_save("ch_yu.png", yu)
        #normal_save("ch_ca.png", ca)
        #normal_save("ch_cb.png", cb)

        bitmap = decode(ca, cb, n_block)
        bitmap_sum += bitmap

        if ref_bitmap is not None:
            count = np.count_nonzero(ref_bitmap == bitmap)
            ratio = count / bitmap.size * 100.0
            print("%s: %d (%.2f%%)" % (cap_path, count, ratio))

    bitmap = (bitmap_sum / len(args.targets) > 0.5).astype(np.uint8)
    if ref_bitmap is not None:
        count = np.count_nonzero(ref_bitmap == bitmap)
        ratio = count / bitmap.size * 100.0
        print("TOTAL: %d (%.2f%%)" % (count, ratio))
    else:
        print(bitmap.flatten())
        cv2.imwrite("bitmap.png", bitmap * 255)

if __name__ == "__main__":
    main()
