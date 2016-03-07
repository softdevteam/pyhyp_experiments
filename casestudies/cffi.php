<?php{
$cffi = import_py_mod("cffi");
$sys = import_py_mod("sys");
$builtin = import_py_mod("__builtin__");
$builtin->setattr($sys, "prefix", "");
$builtin->setattr($sys, "exec_prefix", "");
$builtin->setattr($cffi, "prefix", "");
$verifier = import_py_mod("cffi.verifier");
$verifier->set_tmpdir("/tmp");
$ffi = new $cffi->FFI();
$ffi->cdef("double _clock_gettime_monotonic();");
$csrc = <<<EOD
  #include <time.h>
  #include <math.h>
  #include <stdlib.h>
  double _clock_gettime_monotonic(){
    struct timespec ts;
    if ((clock_gettime(CLOCK_MONOTONIC, &ts)) == -1) {
      err(1, "clock_gettime error");
    return ts.tv_sec + ts.tv_nsec * pow(10, -9);
  }
EOD;
$ffi->set_source("_example", $csrc);
$C = $ffi->dlopen(null);
echo "Monotonic time: " . $C->_clock_gettime_monotonic() . "\n";
}

?>
