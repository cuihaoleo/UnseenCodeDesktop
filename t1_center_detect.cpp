#include "opencv2/core.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/imgproc.hpp"
#include "opencv2/xfeatures2d.hpp"

#include <vector>
#include <iostream>
#include <cmath>

std::vector<cv::Point> detect_box(const cv::Mat &img,
                                  double min_area_ratio=0.1,
                                  double rect_similarity=0.85,
                                  int approx_poly_round=10) {
    cv::Mat gray;
    cv::Mat binary;
    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;

    if (img.channels() == 3)
        cv::cvtColor(img, gray, cv::COLOR_BGR2GRAY);
    else
        gray = img;

    cv::threshold(gray, binary, 0, 255, cv::THRESH_BINARY | cv::THRESH_OTSU);
    //cv::threshold(gray, binary, 200, 255, cv::THRESH_BINARY);
    cv::imwrite("binary.png", binary);
    cv::findContours(binary, contours, hierarchy, cv::RETR_LIST, cv::CHAIN_APPROX_SIMPLE);

    double min_area = img.cols * img.rows * min_area_ratio;

    std::vector<cv::Point> best_ct;
    cv::RotatedRect best_box(cv::Point(0, 0), cv::Size(0, 0), 0);

    for (auto ct: contours) {
        std::vector<cv::Point> hull;
        cv::convexHull(ct, hull);
        double area = cv::contourArea(hull);

        // approx
        cv::RotatedRect b = cv::minAreaRect(hull);

        if (b.size.area() > best_box.size.area()
                && area / b.size.area() > rect_similarity
                && area > min_area) {
            best_box = b; 
            best_ct = hull;
        }
    }

    if (best_ct.size() == 0)
        return best_ct;

    // exact
    std::vector<cv::Point> approx;
    double min_epsilon = 0.0;
    double max_epsilon = 0.2;
    double ref_len = std::sqrt(best_box.size.area());

    for (int round=0; round<approx_poly_round; round++) {
        float epsilon = (min_epsilon + max_epsilon) / 2.0;
        cv::approxPolyDP(best_ct, approx, epsilon * ref_len, true);
        printf("epsilon: %f, num of approx: %lu\n", epsilon, approx.size());

        if (approx.size() == 4)
            break;
        else if (approx.size() > 4)
            min_epsilon = epsilon;
        else
            max_epsilon = epsilon;

        approx.empty();
    }

    if (approx.size() == 4)
        return approx;
    else
        return std::vector<cv::Point>();
}

int main(int argc, char *argv[]) {
    cv::Mat img = cv::imread(argv[1], cv::IMREAD_GRAYSCALE);
    auto ct = detect_box(img);
    std::cout << ct << std::endl;

    cv::drawContours(img, std::vector<std::vector<cv::Point>>(1, ct), -1, 1, 2);
    cv::imwrite("disp.png", img);

    return 0;
}
