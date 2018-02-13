# Installez findlib http://projects.camlcity.org/projects/findlib.html
# et ensuite Archimedes https://forge.ocamlcore.org/projects/archimedes/
# Configuration dans Makefile.conf.  Vous ne devriez pas avoir à
# modifier ce fichier.

include Makefile.conf

SOURCES = $(addprefix src/, $(PROGRAMS))

COMMA=,
NULLSTRING=
SPACE=$(NULLSTRING) #
ifneq ($(strip $(AUTHORS)),)
  PROCESSED_AUTHORS=$(subst $(SPACE),_,$(subst $(COMMA),,$(AUTHORS)))
else
  $(error Please fill the AUTHORS in Makefile.conf)
endif

CURRENT_DIR = $(notdir $(shell pwd))
TARBALL	    = $(TP)-$(PROCESSED_AUTHORS).tar.gz
OCAMLBUILD  = ocamlbuild -use-ocamlfind $(OCAMLFLAGS)

default: all

.PHONY: all byte native
all: $(BEST)

byte: $(SOURCES)
# 	Compile all sources at once (faster & correct symlinks)
	$(OCAMLBUILD) -pkg "$(OCAMLPACKS)" $(SOURCES:.ml=.byte)
$(SOURCES:.ml=.byte): %.byte: %.ml
	$(OCAMLBUILD) -pkg "$(OCAMLPACKS)" $@

native: $(SOURCES)
	$(OCAMLBUILD) -pkg "$(OCAMLPACKS)" $(SOURCES:.ml=.native)
$(SOURCES:.ml=.native): %.native: %.ml
	$(OCAMLBUILD) -pkg "$(OCAMLPACKS)" $@


.PHONY: tar dist clean
# Make a tarball
tar dist: clean
	touch "$(TARBALL)"
	cd .. && tar --dereference --exclude="*~" --exclude="*.tar.gz" \
	  --exclude="._*" --exclude=".DS_Store" \
	  --exclude="doc/*.html" --exclude="doc/*.css" \
	  -zcvf "$(CURRENT_DIR)/$(TARBALL)" "$(CURRENT_DIR)"

clean::
	ocamlbuild -clean
	-$(RM) -r $(wildcard *~ *.tar.gz) *.docdir
	$(RM) $(wildcard $(addprefix doc/, *.html *.css *.aux *.log))
