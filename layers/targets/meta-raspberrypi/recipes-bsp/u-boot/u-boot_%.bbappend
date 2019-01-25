FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

SRC_URI_append = " \
    file://disable-console.patch \
"

#    file://bcm2837-rpi-3-b.dts.patch
#    file://rpi_3_32b_defconfig.patch 
