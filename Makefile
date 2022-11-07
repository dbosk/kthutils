SUBDIR_GOALS=all clean distclean

SUBDIR+=	src/kthutils
SUBDIR+=	doc
SUBDIR+=	tests

version=$(shell sed -n 's/^ *version *= *\"\([^\"]\+\)\"/\1/p' pyproject.toml)

.PHONY: all publish

all:

publish: all
	poetry build
	poetry publish
	git push
	gh release create -t v${version} v${version} doc/kthutils.pdf


.PHONY: clean distclean
clean:
distclean:
	${RM} -Rf dist

INCLUDE_MAKEFILES=makefiles
include ${INCLUDE_MAKEFILES}/subdir.mk
