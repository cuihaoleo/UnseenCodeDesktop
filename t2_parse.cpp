extern "C" {
#include "unseencode.h"
}
#include "us_barcode.hpp"

//#include "opencv2/core.hpp"
//#include "opencv2/highgui.hpp"
//#include "opencv2/imgproc.hpp"
#include "opencv2/core/core.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/imgproc/imgproc.hpp"

#include <iostream>
#include <vector>
#include <array>
#include <cassert>

int main(int argc, char *argv[]) {
    std::vector<std::string> args;
    std::array<int, CLEN> vote{};
    args.assign(argv + 1, argv + argc);

    if (argc < 2)
        throw std::runtime_error("BAD");

    for (auto fpath: args) {
        cv::Mat bgr = cv::imread(fpath, cv::IMREAD_COLOR);
        auto p = preproc(bgr);
        std::vector<bool> raw = decode(p.first, p.second, BLOCK_N);

        std::cout << fpath << std::endl;
        for (size_t i=0; i!=raw.size(); i++) {
            std::cout << (int)raw[i];
            vote[i] += raw[i];
        }
        std::cout << std::endl;
    }

    std::vector<bool> full;
    for (auto item: vote)
        full.push_back(item * 2 > argc - 1);

    std::cout << "ALL:" << std::endl;
    for (int i=0; i<CLEN; i++) {
        std::cout << (int)full[i];
    }
    std::cout << std::endl;

    uint8_t code[TOTAL_BIT];
    std::cout << "CODE:" << std::endl;
    for (int i=0; i<TOTAL_BIT; i++) {
        code[i] = full[PREFIX_LEN + i];
        std::cout << (int)code[i];
    }
    std::cout << std::endl;

    char *msg2 = unseencode_decode(code);
    std::cout << msg2 << std::endl;
    free(msg2);

    return 0;
}
