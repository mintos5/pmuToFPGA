#include "systemc.h"

SC_MODULE(cpuType)          // module (class) declaration
{
  sc_in<int> a, b;        // ports
  sc_out<int> sum, data_out, virtual_tx_valid;

  SC_CTOR(adder)          // constructor
  {
  }
};