FILESEXTRAPATHS_prepend := "${THISDIR}/files:${THISDIR}/patches:"

SRC_URI_append = " \
    file://board/laird/common/Makefile \
    file://board/laird/common/board.c \
    file://board/laird/common/mac_eeprom.c \
    file://board/laird/common/video_display.c \
    file://board/laird/wb50n/Kconfig \
    file://board/laird/wb50n/MAINTAINERS \
    file://board/laird/wb50n/Makefile \
    file://board/laird/wb50n/wb50n.c \
    file://configs/wb50n_mmc_defconfig \
    file://include/configs/wb50n.h \
    file://Makefile.patch \
    file://arch-arm-dts-Makefile.patch \
    file://arch-arm-mach-at91-Kconfig.patch \
"

do_copy_laird_config() {
    rm -rf ${S}/board/laird/wb50n
    cp -r ${WORKDIR}/board/laird/common ${S}/board/laird
    cp -r ${WORKDIR}/board/laird/wb50n ${S}/board/laird
    # cp ${WORKDIR}/arch/arm/dts/at91-wb50n.* ${S}/arch/arm/dts
    cp ${WORKDIR}/configs/wb50n_mmc_defconfig ${S}/configs
    cp ${WORKDIR}/include/configs/wb50n.h ${S}/include/configs
}

do_configure_prepend() {
    do_copy_laird_config
}

PR = "r2"
