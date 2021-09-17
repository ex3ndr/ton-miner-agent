cat ./fpga/sha256_util.cl > ./fpga/fpga.cl
cat ./fpga/sha256_impl.cl >> ./fpga/fpga.cl
cat ./fpga/miner.cl >> ./fpga/fpga.cl
mkdir -p build
cd build
v++ -t sw_emu --platform xilinx_u200_gen3x16_xdma_1_202110_1 -c -k do_work -o'miner.sw_emu.xo' ../fpga/fpga.cl
v++ -t sw_emu --platform xilinx_u200_gen3x16_xdma_1_202110_1 --link miner.sw_emu.xo -o'miner.sw_emu.xclbin'
v++ -t hw_emu --platform xilinx_u200_gen3x16_xdma_1_202110_1 -c -k do_work -o'miner.hw_emu.xo' ../fpga/fpga.cl
v++ -t hw_emu --platform xilinx_u200_gen3x16_xdma_1_202110_1 --link miner.hw_emu.xo -o'miner.hw_emu.xclbin'
v++ -t hw --platform xilinx_u200_gen3x16_xdma_1_202110_1 -c -k do_work -o'miner.xo' ../fpga/fpga.cl
v++ -t hw --platform xilinx_u200_gen3x16_xdma_1_202110_1 --link miner.xo -o'miner.xclbin'