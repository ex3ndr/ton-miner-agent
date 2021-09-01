set -e
node ./config.js $1
diskutil eject /dev/disk2