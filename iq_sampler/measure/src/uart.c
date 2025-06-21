//------------------------------------------------------------------
// Setup UARTE to PC
//------------------------------------------------------------------

#define SPI_BUFFER_SIZE 10
static nrfx_uarte_t instance = NRFX_UARTE_INSTANCE(0);
static nrfx_spis_t instance_spi = NRFX_SPIS_INSTANCE(0); // SPI instance

//SPI Buffers
static uint8_t rx_buffer[SPI_BUFFER_SIZE];
static uint8_t tx_buffer[SPI_BUFFER_SIZE];
volatile bool transfer_done = false; //Bool to indicate SPI transfer done
volatile bool first = true; //Bool to indicate SPI transfer done

void uart_put_char(uint8_t ch);
void uart_put_string(const char * string);

void uart_init(void){
    nrfx_uarte_config_t config = NRFX_UARTE_DEFAULT_CONFIG(TXD_PIN, RXD_PIN);
    config.baudrate            = NRF_UARTE_BAUDRATE_115200;
    nrfx_err_t err = nrfx_uarte_init(&instance, &config, NULL);
}

void uart_uninit(void){
    nrfx_uarte_uninit(&instance);
}

// SPI event handler
void spis_event_handler(nrfx_spis_evt_t const *p_event, void *p_context) {
    if (p_event->evt_type == NRFX_SPIS_XFER_DONE) {
        transfer_done = true;
        uart_put_string("SPI XFER DONE\n");
        char msg[64];
        snprintf(msg, sizeof(msg), "SPI XFER DONE, RX: %d, TX: %d\n",
                 (int)p_event->rx_amount, (int)p_event->tx_amount);
        uart_put_string(msg);
        char buf[10];
        for (int i = 0; i < p_event->rx_amount; i++) {
        snprintf(buf, sizeof(buf), "%02X ", rx_buffer[i]);
        uart_put_string(buf);
}
    }
    else if(p_event->evt_type == NRFX_SPIS_BUFFERS_SET_DONE) {
      uart_put_string("BUFFER SET DONE\n");
    }
}
//SPI Initialization
void spi_init(void){
  nrfx_spis_config_t spi_config = NRFX_SPIS_DEFAULT_CONFIG(SCK_PIN,MOSI_PIN,MISO_PIN,SS_PIN);
    spi_config.mode = NRF_SPIS_MODE_0;
    spi_config.bit_order = NRF_SPIS_BIT_ORDER_MSB_FIRST;

    nrfx_err_t err = nrfx_spis_init(&instance_spi, &spi_config, spis_event_handler, NULL);
    if (err != NRFX_SUCCESS) {
    uart_put_string("SPI init failed!\n");
  }
}

void spi_uninit(void){
  nrfx_spis_uninit(&instance_spi);
}
// Setting interrupts manually
static void manual_isr_setup()
{
	IRQ_DIRECT_CONNECT(SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0_IRQn, 0, nrfx_spis_0_irq_handler, 0);
	irq_enable(SPIM0_SPIS0_TWIM0_TWIS0_SPI0_TWI0_IRQn);
}
//Testing correct initialization of SPI
int test_spi(void){
  if(!nrfx_spis_init_check(&instance_spi)){
    return 0;
  }
  return 1;
}

//Read value of the chip select pin, if low SPI is being communicated
bool read_cs_state_raw(void) {
    return (NRF_P0->IN & (1 << 12)) != 0;  // true = HOOG, false = LAAG
}
//Empty the buffers for SPI communication
int set_spi_buffer(void){
  memset(rx_buffer, 0, SPI_BUFFER_SIZE);
  transfer_done = false;
  /*if(!read_cs_state_raw()){
    return 1;
  }
  if(transfer_done){
    return 1;
  }*/
  uart_put_string("YDit gebeurt");
  nrfx_err_t err = nrfx_spis_buffers_set(&instance_spi, rx_buffer, SPI_BUFFER_SIZE, tx_buffer, SPI_BUFFER_SIZE);
  if(err == NRFX_SUCCESS){
    uart_put_string("Dit gebeurt?");
    return 1;
  }
  else{
    return 0;
  }

}
//Test: delete later
void fake_measurement_and_json(char *json_out, size_t max_len) {
    float distance = 123.45f;
    const char *unit = "cm";

    // Bouw de JSON-string zelf
    snprintf(json_out, max_len, "{\"distance\":%.2f,\"unit\":\"%s\"}", distance, unit);
}
// Read from the SPI buffer
void spi_get_buffer(void){
  if(read_cs_state_raw()){
    uart_put_string("CS hoog");
  }
  while(!transfer_done && !first);
  first = false;
  char buf[10];
  for (int i = 0; i <10; i++) {
      snprintf(buf, sizeof(buf), "%02X ", rx_buffer[i]);
      uart_put_string(buf);}
  if (strncmp((char *)rx_buffer, "START", 5) == 0) {
    uart_put_string("JA");
    memset(tx_buffer, 0, SPI_BUFFER_SIZE);
    fake_measurement_and_json((char *)tx_buffer, SPI_BUFFER_SIZE);
  }
  else{
    uart_put_string("Ontvangen: ");
    char buf[10];
    for (int i = 9; i > 0; i--) {
        snprintf(buf, sizeof(buf), "%02X ", rx_buffer[i]);
        uart_put_string(buf);}
    uart_put_string("NEE");
  }
}

// Sending string over UART
void uart_put_string(const char * string)
{
  while (*string != '\0')
  {
    uart_put_char(*string++);
  }
}

int uart_cbprint(int ch, void * ctx){
  nrfx_uarte_tx(&instance, &ch, 1, 0);
}

void uart_put_char(uint8_t ch)
{
  nrfx_uarte_tx(&instance, &ch, 1, 0);
}

bool uart_chars_available(void)
{
  return nrfx_uarte_rx_ready(&instance, NULL);
}

void uart_get_char(uint8_t * p_ch)
{
  nrfx_uarte_errorsrc_get(&instance);
  nrfx_uarte_rx(&instance, p_ch, 1);
}

void uart_get_string(char *buf, size_t max_len) {
    if (max_len < 4) return;  // 3 + null terminator
    nrfx_err_t err = nrfx_uarte_rx(&instance, (uint8_t *)buf, 3);
    if (err != NRFX_SUCCESS) {
      uart_put_string("RX error\n");
      return;
    }

    buf[3] = '\0';
}

void dist_to_json(char *str, float f){

  int d = ((int)1000*f);
  cbprintf(&uart_cbprint, 0, "\"%s\" : %d",str, d);
}

void int_to_json(char *str, int d){
  cbprintf(&uart_cbprint, 0, "\"%s\" : %d",str, d);
}

void tones_to_json(char * str, float *array,uint32_t length){

  uart_put_string("\"");
  uart_put_string(str);
  uart_put_string("\":[");
  for (uint32_t i = 0; i < length; i++)
  {
    //- Assume 10-bit ADC, and scale resolution to 15-bit, should be more than enough precision
    int f = ((int)32*array[i]);
    cbprintf(&uart_cbprint, 0, "%d", f);

    if ((i + 1) < length)
    {
      uart_put_string(",");
    }
  }
  uart_put_string("]");
}

void uint8array_to_json(char * str, uint8_t *array,uint32_t length){

  uart_put_string("\"");
  uart_put_string(str);
  uart_put_string("\":[");
  for (uint32_t i = 0; i < length; i++)
  {

    cbprintf(&uart_cbprint, 0, "%u", array[i]);

    if ((i + 1) < length)
    {
      uart_put_string(",");
    }
  }
  uart_put_string("]");
}

void sinr_to_json(char * str, nrf_dm_sinr_indicator_t *array,uint32_t length){

  uart_put_string("\"");
  uart_put_string(str);
  uart_put_string("\":[");
  for (uint32_t i = 0; i < length; i++)
  {

    cbprintf(&uart_cbprint, 0, "%d", ((int)array[i]));

    if ((i + 1) < length)
    {
      uart_put_string(",");
    }
  }
  uart_put_string("]");
}

void nrf_dm_report_to_json(nrf_dm_report_t *dm_report,float distance,int32_t duration, uint8_t *hopping_sequence){
  uart_put_string("{");

  //- Print tones

  tones_to_json("i_local",&dm_report->iq_tones->i_local[0],80); uart_put_string(",");
  tones_to_json("q_local",&dm_report->iq_tones->q_local[0],80); uart_put_string(",");
  tones_to_json("i_remote",&dm_report->iq_tones->i_remote[0],80); uart_put_string(",");
  tones_to_json("q_remote",&dm_report->iq_tones->q_remote[0],80); uart_put_string(",");
  uint8array_to_json("hopping_sequence",hopping_sequence,NRF_DM_CHANNEL_MAP_LEN); uart_put_string(",");


  //- Print tone_sinr
  sinr_to_json("sinr_local",&dm_report->tone_sinr_indicators.sinr_indicator_local[0],80); uart_put_string(",");
  sinr_to_json("sinr_remote",&dm_report->tone_sinr_indicators.sinr_indicator_remote[0],80); uart_put_string(",");

  //- Print ranging mode
  //- Print distance
  dist_to_json("ifft[mm]",dm_report->distance_estimates.mcpd.ifft);uart_put_char(',');
  dist_to_json("phase_slope[mm]",dm_report->distance_estimates.mcpd.phase_slope);uart_put_char(',');
  dist_to_json("rssi_openspace[mm]",dm_report->distance_estimates.mcpd.rssi_openspace);uart_put_char(',');
  dist_to_json("best[mm]",dm_report->distance_estimates.mcpd.best);uart_put_char(',');
  dist_to_json("highprec[mm]",distance);uart_put_char(',');

  //- Status params
  int_to_json("link_loss[dB]",dm_report->link_loss); uart_put_char(',');
  int_to_json("duration[us]",duration); uart_put_char(',');
  int_to_json("rssi_local[dB]",dm_report->rssi_local); uart_put_char(',');
  int_to_json("rssi_remote[dB]",dm_report->rssi_remote); uart_put_char(',');
  int_to_json("txpwr_local[dB]",dm_report->txpwr_local); uart_put_char(',');
  int_to_json("txpwr_remote[dB]",dm_report->txpwr_remote); uart_put_char(',');
  int_to_json("quality",dm_report->quality);
  uart_put_string("}\n");
}