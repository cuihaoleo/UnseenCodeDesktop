## UnseenCodeDesktop

UnseenCode embedding & extraction demo code.

### Note

Code in this repo was used to conduct experiments explained in our paper.

This is not an out-of-box demo. You will find that some parts missing to implement the whole embedding-extraction pipeline, and some parameters are hard-encoded in our code.

All programs are originally tested in Arch Linux and MSYS2.

[UnseenCodeCamera2](https://github.com/cuihaoleo/UnseenCodeCamera2) is a full extractor demo. It should be used with the embedding code in this repo.

### Compile

Dependency:

- OpenCV 4.x
- SDL2

For C/C++ code, make them:

```bash
$ make s1_gen_msg
$ make wtmk_disp
$ make t1_center_detect
$ make t2_parse
```

For Python scripts, please use python 3.x.

### Pipeline

Some example input/output files can be found in the `res/` folder.

Embedding:

- Step 1 (Optional): `s1_gen_msg.c`
  - Encode string into binary with BCH error-correction and CRC error-detection.
  - `./s1_gen_msg STRING_TO_ENCODE`
- Step 2: `s2_gen_mask.py`
  - Generate the barcode mask representing the binary string given by user.
  - Run `./s2_gen_mask.py`  and paste the binary obtained from `s1_gen_msg`.
  - Output: `bitmap_orig.png` and `mask.png`.
- Step 3: `s3_color4.py`
  - Generate a pair of barcode images from the given cover image and barcode mask.
  - `./s3_color4.py lena.png mask.png`
  - Output: `out1.png`, `out2.png` by default.

- Step 4: `wtmk_disp.c`
  - A simple player to display the barcode images.
  - `./wtmk_disp out1.png out2.png`

Extraction:

- Step 1a: `crop_img.py`
  - Helper script to crop screen area by hand.
  - `./crop_img.py cap.jpg`
  - Output: `cap_correct.png`
- Step 1b: `t1_center_detect.cpp`
  - Illustrates how auto screen crop works. Full code is integrated into Android demo. This program just output an image outlining the screen area.
  - `./t1_center_detect cap.jpg`
  - Output is `disp.png`.
- Step 2: `t2_parse4pp.py`
  - Extracting UnseenCode.
  - `./t2_parse4pp.py --ref bitmap_orig.png cap_correct.png`
  - Or:  `./t2_parse4pp.py --block 17 cap_correct.png`
- Step 3 (Optional): BCH & CRC decode.

