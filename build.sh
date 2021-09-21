set -e
mkdir -p build
cd build
PLATFORM="${AWS_PLATFORM:-xilinx_u200_gen3x16_xdma_1_202110_1}"

v++ -t sw_emu --platform $PLATFORM -R 1 --connectivity.nk do_work:1 -c -k do_work -o'miner.sw_emu.xo' ../fpga/fpga.cl
v++ -t sw_emu --platform $PLATFORM -R 1 --connectivity.nk do_work:1 --link miner.sw_emu.xo -o'miner.sw_emu.xclbin'
# v++ -t hw_emu --platform $PLATFORM -R 1 --connectivity.nk do_work:1 -c -k do_work -o'miner.hw_emu.xo' ../fpga/fpga.cl
# v++ -t hw_emu --platform $PLATFORM -R 1 --connectivity.nk do_work:1 --link miner.hw_emu.xo -o'miner.hw_emu.xclbin'