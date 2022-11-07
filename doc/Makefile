.PHONY: all
all: kthutils.pdf

LATEXFLAGS+=	-shell-escape
TEX_PYTHONTEX=	yes
PYTHONTEXFLAGS=	--interpreter "python:poetry run python3"

kthutils.pdf: preamble.tex abstract.tex ../LICENSE

kthutils.pdf: ../src/kthutils/ug.tex
kthutils.pdf: ../src/kthutils

../src/kthutils::
	${MAKE} -C $@ all

../%::
	${MAKE} -C $(dir $@) $(notdir $@)


.PHONY: clean
clean:
	${RM} kthutils.pdf
	${MAKE} -C ../src/kthutils clean

.PHONY: distclean
distclean:
	${RM} -Rf __pycache__
	${MAKE} -C ../src/kthutils distclean



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/tex.mk
