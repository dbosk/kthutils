.PHONY: all
all: kthutils.pdf

LATEXFLAGS+=	-shell-escape
TEX_PYTHONTEX=	yes
PYTHONTEXFLAGS=	--interpreter "python:poetry run python3"

kthutils.pdf: preamble.tex abstract.tex ../LICENSE

kthutils.pdf: ../src/kthutils/cli.tex
kthutils.pdf: ../src/kthutils/ug.tex
kthutils.pdf: ../src/kthutils/participants.tex
kthutils.pdf: ../src/kthutils/iprange.tex
kthutils.pdf: ../src/kthutils/forms.tex
kthutils.pdf: ../src/kthutils/onedrive.tex
kthutils.pdf: ../src/kthutils/stayawhile.tex
kthutils.pdf: ../src/kthutils

../src/kthutils::
	${MAKE} -C $@ all

# The woven .tex files must depend on their .nw sources: the generic rule
# below has no prerequisites, so it only runs when a .tex is missing and
# would leave a stale weave in place after a .nw edit.
../src/kthutils/%.tex: ../src/kthutils/%.nw
	${MAKE} -C ../src/kthutils $*.tex

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
