MODULES+=	cli.py
MODULES+=	credentials.py
MODULES+=	ug.py
MODULES+=	participants.py
MODULES+=	iprange.py iprange.sh
MODULES+=	forms.py

.PHONY: all
all: ${MODULES}

credentials.py: cli.nw
	${NOTANGLE.py}

funka-extra-time.sh: participants.nw
	${NOTANGLE.sh}

iprange.py: iprange.sh
iprange.sh: iprange.nw
	${NOTANGLE.sh}
	chmod +x $@

.PHONY: clean
clean:
	${RM} -R ${MODULES} __pycache__
	${RM} *.tex
	${RM} funka-extra-time.sh

INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
