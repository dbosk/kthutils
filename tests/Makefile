define find_tests
find ../src -type f | xargs grep "<<test [^.]*\.py>>" | \
	sed -En "s/^(.*):.*<<test ([^.]*).py>>.*/test_\2.py:\1/p" | sort -u
endef

define def_target
$(shell echo $1 | cut -d: -f1): $(shell echo $1 | cut -d: -f2)
	notangle ${NOTANGLEFLAGS.py} "-R$$(shell echo $$@ | sed 's/_/ /')" $$^ > $$@
endef

TESTS=	$(shell ${find_tests})

DEBUG=

NONLIVE_MARK_EXPR=	-m "not live"
LIVE_MARK_EXPR=		-m "live"

# The default test run is hermetic: it deselects tests marked `live`, so it
# never touches KTH or other external services. Use the `live`/`kth_live`
# targets to run the end-to-end tests against the real services.
.PHONY: all
all: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	poetry run pytest ${NONLIVE_MARK_EXPR} $(if ${DEBUG},--pdb)

.PHONY: live
live: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	poetry run pytest ${LIVE_MARK_EXPR} $(if ${DEBUG},--pdb)

.PHONY: kth_live
kth_live: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	poetry run pytest -m "kth_live" $(if ${DEBUG},--pdb)

$(foreach files,${TESTS},$(eval $(call def_target, ${files})))

.PHONY: clean
clean:
	${RM} $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	${RM} -Rf __pycache__

.PHONY: distclean
distclean:



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
