const fs = require('fs');
const aiName = process.argv[process.argv.length - 1];

(async () => {

    console.log('Waiting for device...');
    while(!fs.existsSync('/Volumes/HIVE/rig.conf')) {
        await new Promise(resolve => setTimeout(resolve, 1000))
    }

    console.log('Writing config...');
    fs.writeFileSync('/Volumes/HIVE/rig.conf', `
    WORKER_NAME=${aiName}
    
    # Common parameters
    HIVE_HOST_URL="http://api.hiveos.farm"
    FARM_HASH=213964f99196f371e7018feff4f393d78f7f2634
    RIG_PASSWD=veBYQD7QJJMppvsgNXXA7P4FykArvyykE64bbuaG6eZzinUHoDqoYTuK9oowrJCZ
    SET_RIG_PASS=1
    `);
    console.log('Unmounting...');
})()