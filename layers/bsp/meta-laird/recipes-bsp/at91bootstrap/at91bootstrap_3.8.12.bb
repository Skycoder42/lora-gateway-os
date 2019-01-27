require at91bootstrap.inc

LIC_FILES_CHKSUM = "file://main.c;endline=27;md5=a2a70db58191379e2550cbed95449fbd"

COMPATIBLE_MACHINE = '(rg1xx-sd)'

SRC_URI = "https://github.com/linux4sam/at91bootstrap/archive/v${PV}.tar.gz;name=tarball"
FILESEXTRAPATHS_prepend := "${THISDIR}/patches:"

# LORIX One board files
SRC_URI_append = " \
    file://contrib/board/laird/wb50n/Config.in.board \
    file://contrib/board/laird/wb50n/Config.in.boardname \
    file://contrib/board/laird/wb50n/Config.in.linux_arg \
    file://contrib/board/laird/wb50n/board.mk \
    file://contrib/board/laird/wb50n/wb50n.c \
    file://contrib/board/laird/wb50n/wb50n_sd_uboot_defconfig \
    file://contrib/board/laird/wb50n/wb50n.h \
"

# Patches
SRC_URI_append = " \
   file://Makefile.patch \ 
   file://contrib-board-Config.in.board.patch \
   file://contrib-board-Config.in.boardname.patch \
   file://contrib-board-Config.in.linux_arg.patch \
   file://contrib-include-contrib_board.h.patch \
   file://add-lpddram1_initalize.patch \
   file://driver-board_hw_info.c.patch \
   file://include-board_hw_info.h.patch \
"

PR = "r1"

SRC_URI[tarball.md5sum] = "9cdcd5b427a7998315e9a0cad4488ffd"
SRC_URI[tarball.sha256sum] = "871140177e2cab7eeed572556025f9fdc5e82b2bb18302445d13db0f95e21694"

