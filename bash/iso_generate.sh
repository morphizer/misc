#!/bin/bash

MREPO_SERVER="http://mrepo"

# Loop over all the ks files in kickstart directory
for iso in $(ls -1 kickstart/); do
  
  # Temporary directory creation
  [ -d ${iso}_tmp/ ] && rm -rf ${iso}_tmp/
  mkdir ${iso}_tmp

  # wget the isolinux directory. We do a cut on the iso variable which gives us either ol6/rhel6/ol5/rhel6 to help
  # point at the right disc. The disc is mounted on the mrepo server, check the url if you're adding something new.
  cd ${iso}_tmp
  wget -r -nd -np -P ./isolinux --quiet --reject "index.html*" ${MREPO_SERVER}/mrepo/$(echo $iso | cut -d "-" -f 1)-x86_64/disc1/isolinux/
  cd ..

  # Replace the default isolinux.cfg with appropriate ks file. Using , instead of / delimiter
  sed "s,append ks=,append ks=${MREPO_SERVER}/kickstart/${iso} initrd=initrd.img,g" isolinux.cfg > ${iso}_tmp/isolinux/isolinux.cfg

  mkisofs -o ${iso}.iso -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -R -J -V -T ${iso}_tmp
  
done
