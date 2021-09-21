set -e
mkdir -p build
cd build
# v++ -t hw_emu --platform $AWS_PLATFORM -R 1 --connectivity.nk vecadd:1 -c -k vecadd -o'hello_world.aws.xo' ../fpga/hello_world.cl
# v++ -t hw_emu --platform $AWS_PLATFORM -R 1 --connectivity.nk vecadd:1 --link hello_world.aws.xo -o'hello_world.aws.xclbin'

v++ -t sw_emu --platform $AWS_PLATFORM -R 1 --connectivity.nk do_work:1 -c -k do_work -o'miner.sw_emu.xo' ../fpga/fpga.cl
v++ -t sw_emu --platform $AWS_PLATFORM -R 1 --connectivity.nk do_work:1 --link miner.sw_emu.xo -o'miner.sw_emu.xclbin'
v++ -t hw_emu --platform $AWS_PLATFORM -R 1 --connectivity.nk do_work:1 -c -k do_work -o'miner.hw_emu.xo' ../fpga/fpga.cl
v++ -t hw_emu --platform $AWS_PLATFORM -R 1 --connectivity.nk do_work:1 --link miner.hw_emu.xo -o'miner.hw_emu.xclbin'