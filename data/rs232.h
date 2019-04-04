#include "systemc.h"

SC_MODULE(serialType)          // module (class) declaration
{
  sc_in<int> a, b, tx_byte, transmit;        // ports
  sc_out<int> sum;

  SC_CTOR(adder)          // constructor
  {
  }
};