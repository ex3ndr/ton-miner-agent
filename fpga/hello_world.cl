__kernel __attribute__ ((reqd_work_group_size(64, 1, 1))) void vecadd(__global int *A, __global int *B, __global int *C) {
  int idx = get_global_id(0);
  C[idx] = A[idx] + B[idx];
}