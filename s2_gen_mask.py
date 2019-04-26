#!/usr/bin/env python3

import cv2
import numpy as np
import sys
import matplotlib.pyplot as plt
import argparse


def get_base(width):
    base0 = np.array([[0, 0, 1, 1, 0, 0, 1, 1], ] * 8)
    base1 = base0.T

    pts1 = np.float32([[-0.5, -0.5], [7.5, -0.5], [-0.5, 7.5]])
    pts2 = np.float32([[0, width/2], [width/2, 0], [width/2, width]])
    mat = cv2.getAffineTransform(pts1, pts2)

    sign0 = cv2.warpAffine(base0, mat, (width, width), flags=cv2.INTER_NEAREST)
    sign1 = cv2.warpAffine(base1, mat, (width, width), flags=cv2.INTER_NEAREST)

    return (mat, sign0, sign1)


def unseencode_bits(block):
    return block ** 2 + (block - 1) ** 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=768, help="Mask width")
    parser.add_argument("--mask", default="mask.png", help="Output mask")
    args = parser.parse_args()

    bin_str = input()
    msg = []
    for c in bin_str:
        msg.append(int(c))
    mlen = len(msg)
    assert mlen == 511

    block = clen = 1
    while clen < len(msg):
        block += 1
        clen = unseencode_bits(block)

    print("B = %d, BITS = %d" % (block, clen))
    prefix_len = (clen - mlen) // 2
    postfix_len = (clen - mlen) - prefix_len

    for i in range(prefix_len):
        msg.insert(0, i & 1)

    for i in range(postfix_len):
        msg.append(i & 1)

    assert(len(msg) == clen)
    msg = np.array(msg, dtype=np.uint8)

    patch_width = args.width // block
    _, sign0, sign1 = get_base(patch_width)
    buf = list(msg)
    
    img = np.zeros((args.width, args.width), dtype=np.float32)
    
    step1 = np.linspace(0, args.width, block, False, dtype=int)
    step2 = np.linspace(0, args.width, 2*block, False, dtype=int)[1:-1:2]
    for step in (step1, step2):
        for sy in step:
            for sx in step:
                bit = buf.pop(0)
                img[sy:sy+patch_width, sx:sx+patch_width] += sign1 if bit else sign0
    
    img = (img * 255.0).astype(np.uint8)
    cv2.imwrite(args.mask, img)
    print(*msg.flatten(), sep="")

    bitmap = msg[:-1].reshape(2*(block-1), block)
    cv2.imwrite("bitmap_orig.png", bitmap * 255)
    

if __name__ == "__main__":
    main()
