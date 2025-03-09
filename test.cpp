%%cuda
#include <cstdio>
#include <iostream>

int main( void ) {
    CPUBitmap bitmap( DIM, DIM );
    unsigned char *ptr = bitmap.get_ptr();
    kernel( ptr );
    bitmap.display_and_exit();
}

void kernel( unsigned char *ptr ){
for (int y=0; y<DIM; y++) {
for (int x=0; x<DIM; x++) {
int offset = x + y * DIM;
int juliaValue = julia( x, y );
ptr[offset*4 + 0] = 255 * juliaValue;
ptr[offset*4 + 1] = 0;
ptr[offset*4 + 2] = 0;
ptr[offset*4 + 3] = 255;
}
}
}