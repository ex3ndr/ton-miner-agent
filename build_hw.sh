set -e
mkdir -p build
cd build
cp ../fpga/fpga.cl source.cl
v++ -t hw --platform $AWS_PLATFORM -R 1 --connectivity.nk do_work:1 -c -k do_work -o'miner.xo' source.cl
v++ -t hw --platform $AWS_PLATFORM -R 1 --connectivity.nk do_work:1 --link miner.xo -o'miner.xclbin'