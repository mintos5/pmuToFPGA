#include "systemc.h"

SC_MODULE(cpuType)          // module (class) declaration
{
  sc_in<int> a, b, virtual_rx_valid;        // ports
  sc_out<int> sum, data_out, virtual_tx_valid;

  SC_CTOR(adder)          // constructor
  {
  }
};