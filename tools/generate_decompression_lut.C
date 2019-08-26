// a c++ program to generate decompression lookup tables
// Usage:
//

#include <iostream>
#include <stdint.h>
#include <string>

#ifdef __ROOT__
#include <TApplication.h>
#include <TCanvas.h>
#include <TGraph.h>
#include <TROOT.h>
#endif
using namespace std;
uint8_t CompressionAlgorithms_compressS0(uint32_t in_val, uint8_t K = 3,
                                         uint8_t M = 0) {
  // taken from CompressionAlgorithms.C in the ASW source code

  if (K > 7 || M > 7 || (K + M) > 8) {
    cout << "Error: K or M value invalid,  K <=7, M<=7 and K+M<=8 " << endl;
    return 0xff;
  }
  uint8_t out_val;
  uint8_t exponent = 1;
  uint8_t mantissa = 0;
  // check if V < 2^(M+1)
  if (in_val < ((uint32_t)1 << (M + 1))) {
    // set C = V and skip
    out_val = (uint8_t)in_val;
  } else {
    // V >= 2^(M+1),
    while (in_val > (((uint32_t)1 << (M + 1)) - 1)) {
      // shift V right until 1's (if any) appear only in LS (M+1) bits
      in_val >>= 1;
      // exponent is number of shifts + 1
      exponent++;
    }

    // cross check for exponent size
    if (exponent > ((1 << K) - 1)) {
      cout << "Exponent size  invalid " << ((1 << K) - 1) << endl;
      return 0xff;
    }
    // mantissa, LS M bits of the shifted value
    mantissa = (uint8_t)(in_val & (((uint32_t)1 << M) - 1));
    // C = m + 2^M * e
    out_val = (uint8_t)(mantissa + (exponent << M));
  }
  return out_val;
}

void makeLUT(uint8_t K, uint8_t M, int max_value, float *x, float *y) {
  unsigned int first_x = 0;
  unsigned int last_x = 0;
  unsigned int last_value = 0;
  unsigned int mean_x = 0;
  unsigned int value = 0;

  cout << "_decompression_LUT_SKM_0" << (unsigned int)K << (unsigned int)M
       << "={" << endl;
  //python format

  for (uint32_t i = 0; i < max_value; i++) {
    uint8_t out = CompressionAlgorithms_compressS0(i, K, M);
    x[i] = i;
    value = (unsigned int)out;
    y[i] = value;

    if (value != last_value) {
      mean_x = (first_x + last_x) / 2;
      cout << last_value << ":" << mean_x << "," << endl;
      first_x = i;
    }
    last_x = i;
    last_value = value;
  }
  cout << "}" << endl;
}

int main(int argc, char *argv[]) {
  uint8_t K = 5;
  uint8_t M = 3;
  int max_value = 65535; //16-bit
  if (argc < 3) {
    cout << "compress code generator" << endl;
    cout << "./main K  M max_value " << endl;
    return 0;
  }
  K = atoi(argv[1]);
  M = atoi(argv[2]);
  if(argc==3){
	  max_value = atoi(argv[3]);
  }
  float *x = new float[max_value];
  float *y = new float[max_value];
  makeLUT(K, M, max_value, x, y);

#ifdef __ROOT__
  TApplication *theApp;
  theApp = new TApplication("app", &argc, argv);
  TCanvas c;
  TGraph g(max_value, x, y);
  g.Draw("ALP");

  theApp->Run();
  delete theApp;
#endif

  delete[] x;
  delete[] y;
  return 0;
}
