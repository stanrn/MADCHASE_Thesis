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


cmake_minimum_required(VERSION 3.20.0)
#add_compile_options(-fno-use-cxa-atexit)


find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(inititator)
#target_link_libraries(app PRIVATE "-fno-use-cxa-atexit" "-fno-rtti")
#set(CONFIG_CPLUSPLUS "n" CACHE STRING "Disable C++")
#set(CMAKE_CXX_FLAGS "-fno-exceptions")


# Disable C++ usage
#set(CMAKE_CXX_STANDARD 98)  # Ensure C++ is not used
#set(CMAKE_CXX_COMPILER "")

target_sources(app PRIVATE   src/main.c)
