mkdir -p build
cd build
# v++ -t hw_emu --platform $AWS_PLATFORM -R 1 --connectivity.nk vecadd:1 -c -k vecadd -o'hello_world.aws.xo' ../fpga/hello_world.cl
# v++ -t hw_emu --platform $AWS_PLATFORM -R 1 --connectivity.nk vecadd:1 --link hello_world.aws.xo -o'hello_world.aws.xclbin'
cp ../fpga/fpga.cl source.cl
v++ -t hw --platform $AWS_PLATFORM -R 1 --connectivity.nk do_work:1 -c -k do_work -o'miner.xo' source.cl
v++ -t hw --platform $AWS_PLATFORM -R 1 --connectivity.nk do_work:1 --link miner.xo -o'miner.xclbin'