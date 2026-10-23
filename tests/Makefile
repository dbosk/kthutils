# Test chunks are named after the file they produce, wrapped in the noweb
# [[...]] quoting that makefiles/noweb.mk expects: <<[[test_forms.py]]>>.
# The brackets make noweave escape the underscore, so the chunk name can be
# the literal filename and no name mangling is needed here.
define find_tests
find ../src -type f -name '*.nw' | xargs grep "<<\[\[test_[^.]*\.py\]\]>>" | \
	sed -En "s/^(.*):.*<<\[\[(test_[^.]*\.py)\]\]>>.*/\2:\1/p" | sort -u
endef

define def_target
$(shell echo $1 | cut -d: -f1): $(shell echo $1 | cut -d: -f2)
	$${NOTANGLE.py}
endef

TESTS=	$(shell ${find_tests})

DEBUG=

PYTESTFLAGS=

# The default run replays recorded responses with the network blocked
# (`addopts` in pyproject.toml); tests marked `live` are skipped.  The
# live targets talk to the real services: they need the KTH credentials,
# STAYAWHILE_API_KEY and, since recorded tests re-record into a temporary
# directory to check for drift, TEST_PSEUDONYM_KEY.  Tests marked
# `mutates` change a service and run only with `live-writes`.
.PHONY: all
all: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	poetry run pytest ${PYTESTFLAGS} $(if ${DEBUG},--pdb)

.PHONY: live
live: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	poetry run pytest --live ${PYTESTFLAGS} $(if ${DEBUG},--pdb)

.PHONY: live-writes
live-writes: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	poetry run pytest --live --live-writes ${PYTESTFLAGS} $(if ${DEBUG},--pdb)

.PHONY: kth_live
kth_live: $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	poetry run pytest --live -m "kth_live" ${PYTESTFLAGS} $(if ${DEBUG},--pdb)

$(foreach files,${TESTS},$(eval $(call def_target, ${files})))

.PHONY: clean
clean:
	${RM} $(foreach files,${TESTS},$(shell echo ${files} | cut -d: -f1))
	${RM} -Rf __pycache__

.PHONY: distclean
distclean:



INCLUDE_MAKEFILES=../makefiles
include ${INCLUDE_MAKEFILES}/noweb.mk
