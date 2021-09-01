source ./aicruncher/h-manifest.conf
tar -zcvf aicruncher-${CUSTOM_VERSION}.tar.gz aicruncher
s3cmd put aicruncher-${CUSTOM_VERSION}.tar.gz s3://ai-model/d06d720f-6633-4300-96ef-664c5beb2e7a/   --acl-public --add-header=Cache-Control:max-age=86400
rm aicruncher-${CUSTOM_VERSION}.tar.gz