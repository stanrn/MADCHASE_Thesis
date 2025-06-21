/*********************************************************************
 *        Copyright (c) 2022 Carsten Wulff Software, Norway
 * *******************************************************************
 * Created       : wulff at 2022-5-28
 * *******************************************************************
 *  The MIT License (MIT)
 *
 *  Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:
 *
 *  The above copyright notice and this permission notice shall be included in all
 *  copies or substantial portions of the Software.
 *
 *  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 *  SOFTWARE.
 *
 ********************************************************************/


//#include <zephyr.h>
//#include <init.h>
#include <nrf.h>
#include <nrfx.h>
#include "nrf_dm.h"
#include "nrfx_config.h"
#include "nrfx_clock.h"
#include "nrfx_uarte.h"
#include "nrfx_spis.h"
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>

// UART PIN config
#ifndef TXD_PIN
#define TXD_PIN 6
#endif

#ifndef RXD_PIN
#define RXD_PIN 8
#endif

// SPI PIN config
#ifndef SS_PIN
#define SS_PIN 12
#endif

#ifndef SCK_PIN
#define SCK_PIN 16
#endif

#ifndef MOSI_PIN
#define MOSI_PIN 14
#endif

#ifndef MISO_PIN
#define MISO_PIN 15
#endif

#include "dm.c"
#include "uart.c"
#include "roles.c"

// Setting config and report variables for distance measurements
static nrf_dm_config_t dm_config;
static nrf_dm_report_t dm_report;

#ifdef __cplusplus
extern "C" {
#endif

void *__dso_handle = 0;

#ifdef __cplusplus
}
#endif

// None of the SPI code is currently implemented
int main(void)
{
  //Initialization
  dm_clock_init();
  debug_init();
  dm_init();

  int current_role = CMD_NONE;
  /*spi_init();
  manual_isr_setup();
  set_spi_buffer();*/
  // Getting first roles
  MeasPair result = read_uart_role();
  current_role = result.role;
  int seed = result.seed + 40;
  // While loop for dynamic role changing
  while(1){
    if (current_role == CMD_INITIATOR){
      result = run_initiator(seed);
      current_role = result.role;
      seed = result.seed + 40;
    } else if (current_role == CMD_REFLECTOR){
      result = run_reflector(seed);
      current_role = result.role;
      seed = result.seed + 40;
    } else if (current_role == CMD_NONE){
      result = run_none(seed);
      current_role = result.role;
      seed = result.seed + 40;
    }
  }
    // Unreachable in normal code
    //spi_uninit();
    return 0;
}

