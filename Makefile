INSTALL_DIR := /usr/local/bin
BUILD_DIR := ./build
SRC_DIR := ./src

BIN := $(BUILD_DIR)/goto
INST_BIN := $(INSTALL_DIR)/goto

S_GOTO := $(SRC_DIR)/goto.py
S_ABOUT := $(SRC_DIR)/about.py
S_TERM_COL := $(SRC_DIR)/term_col.py

release := alpha
level := build
V_LEVEL := 5
V_RELEASE := alpha

ifeq ($(level),major)
	V_LEVEL := 1
else ifeq ($(level),minor)
	V_LEVEL := 2
else ifeq ($(level),patch)
	V_LEVEL := 3
else ifeq ($(level),build)
	V_LEVEL := 5
else
	check_level := $(error Error invalid version level: '$(level)')
endif

ifeq ($(release),alpha)
	V_RELEASE := alpha
else ifeq ($(release),beta)
	V_RELEASE := beta
else ifeq ($(release),rc)
	V_RELEASE := rc
else ifeq ($(release),release)
	V_RELEASE := ""
else
	check_release := $(error Error invalid release type: '$(release)')
endif

VERSION = $(shell grep "^__version__" $(S_ABOUT) | awk -F'"' '{FS="[.-]"; $$0 = $$2;} {($$4 != "$(V_RELEASE)" || $(V_LEVEL) <= 3) ? $$5 = 1 : $$5++} {($(V_LEVEL) != 5) ? $$$(V_LEVEL)++ : $$$(V_LEVEL) = $$$(V_LEVEL); (!"$(V_RELEASE)") ? ver = sprintf("%s.%s.%s", $$1, $$2, $$3) : ver = sprintf("%s.%s.%s-$(V_RELEASE).%d", $$1, $$2, $$3, $$5); print ver}')

.PHONY: all
all: build

.PHONY: tag
tag: version build
	@echo tagging release $(VERSION)
	@git tag -a v$(VERSION) -m "type: $(release), level: $(level), v$(VERSION)"

.PHONY: install
install: build
	@echo installing $(BIN) to $(INST_BIN)
	@cp $(BIN) $(INST_BIN)

.PHONY: build
build: $(S_ABOUT) $(S_GOTO) $(S_TERM_COL)
	@echo building $(BIN)
	@mkdir -p $(BUILD_DIR)
	@echo "#!/usr/bin/env python3" > $(BIN)
	@echo "" >> $(BIN)

# 	about
	@sed '/if __name__/,$$d' $(S_ABOUT) >> $(BIN)

# 	term_col
	@sed '/if __name__/,$$d' $(S_TERM_COL) >> $(BIN)

# 	goto
	@cat $(S_GOTO) >> $(BIN)

# 	formatting & permissions
	@echo formatting $(BIN)
	@isort $(BIN)
	@black $(BIN)
	@chmod +x $(BIN)
	@echo built: $(BIN)

.PHONY: bump
bump:
	@echo updating src version to: $(VERSION)
	@sed -i.bak 's/^__version__ = .*/__version__ = "$(VERSION)"/g' $(S_ABOUT)

.PHONY: undo-bump
undo-bump:
	@echo undoing bump
	@mv $(S_ABOUT).bak $(S_ABOUT)

.PHONY: next-bump
next-bump: $(S_ABOUT) $(S_GOTO) $(S_TERM_COL) current
#	shell grep "^__version__" $(S_ABOUT) | awk -F'"' '{FS="[.-]"; $$0 = $$2;} {($$4 != "$(V_RELEASE)") ? $$5 = 0 : $$5++} {$$$(V_LEVEL)++; printf "%s.%s.%s-$(V_RELEASE).%x", $$1, $$2, $$3, $$5}'
	@echo next version: $(VERSION)

.PHONY: current
current:
	@echo current version: $(shell grep "^__version__" $(S_ABOUT) | awk -F'"' '{print $$2}')

.PHONY: distclean
distclean: clean
	@echo cleaning install bin
	@-rm $(shell which goto)

.PHONY: clean
clean:
	@echo cleaning build directory
	@-rm -r $(BUILD_DIR) 
	@-rm $(S_ABOUT).bak
