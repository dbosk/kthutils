.PHONY: all
all: __init__.py

.INTERMEDIATE: init.py

__init__.py: init.py
	ln $< $@

.PHONY: clean
clean:
	${RM} __init__.py

INCLUDE_MAKEFILES=../../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
