mkdir -p build
cd build
v++ -t hw --platform xilinx_aws-vu9p-f1_shell-v04261818_201920_2 -c -k do_work -o'miner.aws.xo' ../fpga/fpga.cl
v++ -t hw --platform xilinx_aws-vu9p-f1_shell-v04261818_201920_2 --link miner.aws.xo -o'miner.aws.xclbin'