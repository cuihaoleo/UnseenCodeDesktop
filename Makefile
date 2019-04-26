CFLAGS += -Wall -fstack-protector-strong
CXXFLAGS += -Wall -std=c++11 -fstack-protector-strong
INC = -I cpp/ `pkg-config --cflags opencv4`
LIBS = -lm `pkg-config --libs opencv4`

bch.o: cpp/bch.c cpp/bch.h
	$(CC) -c -o $@ $(CFLAGS) $(INC) $<

err_chk.o: cpp/err_chk.c cpp/err_chk.h
	$(CC) -c -o $@ $(CFLAGS) $(INC) $<

unseencode.o: cpp/unseencode.c cpp/unseencode.h
	$(CC) -c -o $@ $(CFLAGS) $(INC) $<

us_barcode.o: cpp/us_barcode.cpp cpp/us_barcode.hpp
	$(CC) -c -o $@ $(CFLAGS) $(INC) $<

s1_gen_msg: s1_gen_msg.c bch.o err_chk.o unseencode.o
	$(CC) -o $@ $(CFLAGS) $(LIBS) $(INC) $^

t1_center_detect: t1_center_detect.cpp
	$(CXX) -o $@ $(CFLAGS) $(LIBS) $(INC) $^

t2_parse: t2_parse.cpp bch.o err_chk.o unseencode.o us_barcode.o
	$(CXX) -o $@ $(CFLAGS) $(LIBS) $(INC) $^
