SECTION = "kernel"
DESCRIPTION = "Linux kernel for Atmel ARM SoCs (aka AT91)"
SUMMARY = "Linux kernel for Atmel ARM SoCs (aka AT91)"
LICENSE = "GPLv2"
LIC_FILES_CHKSUM = "file://COPYING;md5=bbea815ee2795b2f4230826c0c6b8814"

inherit kernel

RDEPENDS_${KERNEL_PACKAGE_NAME}-base = ""
FILESEXTRAPATHS_prepend := "${THISDIR}/${P}:"

SRCREV = "e3185123541204ca4f715eeaaa1f9929c09ff3b4"

PV = "4.19+git${SRCPV}"

S = "${WORKDIR}/git"

KBRANCH = "linux-4.19.y"
SRC_URI = " \
    git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git;protocol=git;branch=${KBRANCH} \
    file://defconfig \
"

python __anonymous () {
	if d.getVar('UBOOT_FIT_IMAGE', True) == 'xyes':
		d.appendVar('DEPENDS', ' u-boot-mkimage-native dtc-native')
}

do_deploy_append() {
	if [ "${UBOOT_FIT_IMAGE}" = "xyes" ]; then
		DTB_PATH="${B}/arch/${ARCH}/boot/dts/"
		if [ ! -e "${DTB_PATH}" ]; then
			DTB_PATH="${B}/arch/${ARCH}/boot/"
		fi

		if [ -e ${S}/arch/${ARCH}/boot/dts/${MACHINE}.its ]; then
			cp ${S}/arch/${ARCH}/boot/dts/${MACHINE}*.its ${DTB_PATH}
			cd ${DTB_PATH}
			mkimage -f ${MACHINE}.its ${MACHINE}.itb
			install -m 0644 ${MACHINE}.itb ${DEPLOYDIR}/${MACHINE}.itb
			cd -
		fi
	fi
}

kernel_do_configure_append() {
	rm -f ${B}/.scmversion ${S}/.scmversion
	cd ${S}; git status; cd -
}

KERNEL_MODULE_AUTOLOAD += "atmel_usba_udc g_serial"
KERNEL_MODULE_PACKAGE_SUFFIX=""

COMPATIBLE_MACHINE = "(rg1xx-sd)"
