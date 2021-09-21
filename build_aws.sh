cd build
rm -fr to_aws
$VITIS_DIR/tools/create_vitis_afi.sh -xclbin=miner.xclbin -o=miner -s3_bucket=some-afi -s3_dcp_key=dcp -s3_logs_key=logs