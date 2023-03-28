MODULES+=	cli.py
MODULES+=	credentials.py
MODULES+=	ug.py

.PHONY: all
all: ${MODULES}

credentials.py: cli.nw
	${NOTANGLE.py}

.PHONY: clean
clean:
	${RM} -R ${MODULES} __pycache__
	${RM} *.tex

INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
