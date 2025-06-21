######################################################################
##        Copyright (c) 2022 Carsten Wulff Software, Norway
## ###################################################################
## Created       : wulff at 2022-5-28
## ###################################################################
##  The MIT License (MIT)
##
##  Permission is hereby granted, free of charge, to any person obtaining a copy
##  of this software and associated documentation files (the "Software"), to deal
##  in the Software without restriction, including without limitation the rights
##  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
##  copies of the Software, and to permit persons to whom the Software is
##  furnished to do so, subject to the following conditions:
##
##  The above copyright notice and this permission notice shall be included in all
##  copies or substantial portions of the Software.
##
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
##  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
##  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
##  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
##  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
##  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
##  SOFTWARE.
##
######################################################################

#-  Copy from https://gist.github.com/sighingnow/deee806603ec9274fd47

# Command to flash devices using this makefile
# make first;make flash1;make flash2
OSFLAG 				:=
ifeq ($(OS),Windows_NT)
	OSFLAG = win
else
	UNAME_S := $(shell uname -s)
	ifeq ($(UNAME_S),Linux)
	OSFLAG = linux
	endif
	ifeq ($(UNAME_S),Darwin)
	OSFLAG = osx
	endif

endif

# Manually enter used node ids
sid_module1 = 685722045
#sid_module2 = 685540671
#sid_module2 = 685367456
sid_module2 = 685775276

current_dir = $(shell pwd)

nrfjprog = nrfjprog.exe

# Manually enter used node ids
ifeq ($(OSFLAG),win)
	pycmd = /usr/bin/python3
	sid_module2 = 685775276
    sid_module1 = 685722045
#   sid_module2 = 685540671
#	sid_module2 = 685367456



else
ifeq ($(OSFLAG),linux)


	nrfjprog = nrfjprog
	pycmd = python3
else
	nrfjprog = nrfjprog
endif
endif

first:
	cd measure; west build -b nrf52833dk_nrf52833 -- -DCONF_FILE=prj.conf

flash1:
	cd measure; west flash -i ${sid_module1}
	${MAKE} -f Makefile reset SID=${sid_module1}

flash2:
	cd measure; west flash -i ${sid_module2}
	${MAKE} -f Makefile reset SID=${sid_module2}

#flash3:
#	cd measure; west flash -i ${sid_module3}
#	${MAKE} -f Makefile reset SID=${sid_module3}

reset:
	${nrfjprog} -p -s ${SID} && ${nrfjprog} -r -s ${SID}


doc:
	pandoc --from gfm README.md -o README.html

clean:
	rm -rf measure/build
