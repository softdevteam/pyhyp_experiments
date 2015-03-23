<?php{
$cffi = import_py_mod("cffi");
$sys = import_py_mod("sys");
$sys->prefix = "";
$sys->exec_prefix = "";
$cffi->prefix = "";
$ffi = new $cffi->FFI();
$ffi->cdef("double _clock_gettime_monotonic();");
$csrc = <<<EOD
  #include <time.h>
  #include <math.h>
  #include <stdlib.h>
  double _clock_gettime_monotonic(){
    struct timespec ts;
    if ((clock_gettime(CLOCK_MONOTONIC_RAW, &ts)) < 0) {
      perror("clock_gettime"); exit(1);
    }
    return ts.tv_sec + ts.tv_nsec * pow(10, -9);
  }
EOD;
$C = $ffi->verify($csrc);
echo "Monotonic time: " . $C->_clock_gettime_monotonic();
}
?>
