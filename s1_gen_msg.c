#include "err_chk.h"

#include <stdio.h>
#include <stdlib.h>

#include "unseencode.h"

int main(int argc, char *argv[]) {
    char *msg;

    if (argc != 2) {
        fprintf(stderr, "Wrong number of arguments!");
        return -1;
    }

    msg = argv[1];
    uint8_t *code = unseencode_encode(msg);
    printf("UnseenCode: ");
    for (int i=0; i<TOTAL_BIT; i++) {
        printf("%hhu", code[i]);
    }
    putchar('\n');

#ifdef DEBUG
    for (int i=0; i<6; i++)
        code[i] ^= 1;
    char *msg2 = unseencode_decode(code);
    puts(msg2);
    free(msg2);
#endif

    free(code);

    return 0;
}
