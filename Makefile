CFLAGS += -Wall -fstack-protector-strong
CXXFLAGS += -Wall -std=c++11 -fstack-protector-strong
INC = -I lib/ `pkg-config --cflags opencv4`
LIBS = -lm `pkg-config --libs opencv4`

bch.o: lib/bch.c lib/bch.h
	$(CC) -c -o $@ $(CFLAGS) $(INC) $<

err_chk.o: lib/err_chk.c lib/err_chk.h
	$(CC) -c -o $@ $(CFLAGS) $(INC) $<

unseencode.o: lib/unseencode.c lib/unseencode.h
	$(CC) -c -o $@ $(CFLAGS) $(INC) $<

us_barcode.o: lib/us_barcode.cpp lib/us_barcode.hpp
	$(CC) -c -o $@ $(CFLAGS) $(INC) $<

s1_gen_msg: s1_gen_msg.c bch.o err_chk.o unseencode.o
	$(CC) -o $@ $(CFLAGS) $(LIBS) $(INC) $^

wtmk_disp: wtmk_disp.cpp
	$(CXX) `pkg-config --libs --cflags sdl2` -lSDL2_image $^

t1_center_detect: t1_center_detect.cpp
	$(CXX) -o $@ $(CFLAGS) $(LIBS) $(INC) $^

t2_parse: t2_parse.cpp bch.o err_chk.o unseencode.o us_barcode.o
	$(CXX) -o $@ $(CFLAGS) $(LIBS) $(INC) $^
