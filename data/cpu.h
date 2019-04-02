#include "systemc.h"

SC_MODULE(cpuType)          // module (class) declaration
{
  sc_in<int> a, b;        // ports
  sc_out<int> sum, nieco;

  void do_add()           // process
  {
    sum.write(a.read() + b.read()); //or just sum = a + b
  }

  SC_CTOR(adder)          // constructor
  {
    SC_METHOD(do_add);    // register do_add to kernel
    sensitive << a << b;  // sensitivity list of do_add
  }
};