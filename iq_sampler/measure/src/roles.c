enum Role {
    CMD_INITIATOR,
    CMD_REFLECTOR,
    CMD_NONE,
    CMD_UNKNOWN = -1
};

typedef struct {
    int role;
    int seed;
} MeasPair;

MeasPair read_uart_role(void){
    uart_init();
    //SPI code not implemented!!
    /*spi_get_buffer();
    uart_put_string("XDit gebeurt");
    if(test_spi() && set_spi_buffer() == 1){
        uart_put_string("SPI INIT AND BUF");
    }
    else if(test_spi()){
        uart_put_string("SPI INIT");
    }
    else{
        uart_put_string("SPI UNINIT");
    }*/
    // Reading the role and seed value from UART, changing role and returning it
    char buf[16]; // Max 1 role + 2 digits seed (e.g., r99) + null
    MeasPair result = { .role = CMD_UNKNOWN, .seed = -1 };
    if (uart_chars_available()){
        uart_get_string(buf, sizeof(buf));
        size_t len = strlen(buf);
        if (len >= 2) {
            if (buf[0] == 'i') {
                result.role = CMD_INITIATOR;
                uart_put_string("Werkt dit?{i_local:[0,0,0,0,3360,608,-5120,3584,-1024,-3200,-160,2080,-320,-160,320,96,-1184,-1952,2624,-3488,2528,-224,1280,4288,3424,1312,-2368,-4256,1024,3168,1472,-1984,-2304,3584,-3040,2528,3648,-2816,-928,-192,-1824,-1216,-2272,-2592,-1632,-2048,1376,-480,2176,-1984,-1120,0,-1856,-1856,-1888,-928,-1920,544,2016,-1376,480,1632,-2176,2368,2592,-2560,-2912,2944,3104,1632,-2176,-3168,-2624,-2528,3296,-352,2400,-672,800,0],q_local:[0,0,0,0,4864,5568,1024,3104,4192,1504,-2880,-160,1312,864,-896,-544,1408,-1504,1408,0,2944,4160,4128,-1088,2848,4320,3776,864,-4128,-2624,-4000,3552,-3232,1856,2336,-2880,800,-2272,3328,3328,-2624,-2816,1792,608,1856,-864,-1632,-2240,96,576,1696,1920,-224,512,-256,-1696,192,-1888,672,-1824,2304,1760,-1472,1312,928,-1216,992,1120,192,-2816,-2336,384,-1920,2112,-160,3168,-2112,3072,-2944,0],i_remote:[0,0,0,0,-1184,3104,3424,2080,3968,480,-2496,1472,768,960,-736,960,608,2272,-2656,3488,-288,3840,4032,-1024,3936,4672,704,-3808,128,3712,2400,-3680,128,224,-3680,3392,-3136,3936,-1696,-1376,2560,608,3296,1952,2848,-1824,-576,-1952,2496,-2464,-2336,-2080,192,320,1856,1824,2304,-1312,-1504,-1152,2720,2496,-2560,3136,3328,-3328,-3584,2688,2560,2848,2944,-160,3392,-192,-3168,-1088,-2528,1216,-2144,0],q_remote:[0,0,0,0,5760,4640,-3648,4064,-960,-3552,1504,1600,-1184,-320,-704,-928,1792,-1088,1600,-928,4064,2272,2272,4608,2688,-1440,-4864,-2912,4608,2688,3808,-2656,4352,-4256,2272,-2560,-5600,1472,3552,3584,-2816,-3424,640,-1568,-1376,-2496,1824,1792,352,-288,-672,-1056,2304,2272,1344,-1504,128,-1984,2048,-2528,1056,1664,-1760,864,544,960,-736,-2656,-2912,-64,1376,3904,2112,4032,-2464,3744,-2944,3680,-3200,0],hopping_sequence:[63,53,77,32,66,6,41,25,38,60,74,42,4,21,7,52,69,35,13,44,16,23,39,37,58,76,48,57,17,36,9,49,45,12,24,10,55,14,29,31,34,50,61,26,15,72,20,40,19,46,8,5,70,59,51,75,43,64,33,27,68,47,78,62,18,71,30,28,73,54,56,67,65,22,11],sinr_local:[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],sinr_remote:[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,2,2,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0],ifft[mm] : 1578,phase_slope[mm] : 6833,rssi_openspace[mm] : 7943,best[mm] : 1578,highprec[mm] : 0,link_loss[dB] : 58,duration[us] : 20087,rssi_local[dB] : 51,rssi_remote[dB] : 49,txpwr_local[dB] : 8,txpwr_remote[dB] : 8,quality : 0}\n)");
            } else if (buf[0] == 'r') {
                result.role =  CMD_REFLECTOR;
            } else if (buf[0] == 'n') {
                result.role = CMD_NONE;
            } else {
                result.role = CMD_UNKNOWN;
            }       
            result.seed = atoi(&buf[1]);  // rest is the number
        }
    }
    uart_uninit();
    return result;  // No new input
}

MeasPair run_initiator(int seed){

    static nrf_dm_config_t dm_config;
    static nrf_dm_report_t dm_report;

    dm_config = NRF_DM_DEFAULT_CONFIG;
    dm_config.role = NRF_DM_ROLE_INITIATOR;
    dm_config.rng_seed = seed;

    while(1){
        // Clear previous result
        dm_report.link_loss = 0;
        dm_report.rssi_local = 0;
        dm_report.rssi_remote = 0;
        dm_report.txpwr_local = 0;
        dm_report.txpwr_remote = 0;
        dm_report.quality = 90;
        dm_report.distance_estimates.mcpd.ifft = 0;
        dm_report.distance_estimates.mcpd.phase_slope = 0;
        dm_report.distance_estimates.mcpd.rssi_openspace = 0;
        dm_report.distance_estimates.mcpd.best = 0;
        for(int i=0;i<80;i++){
        dm_report.iq_tones->i_local[i] =0;
        dm_report.iq_tones->q_local[i] =0;
        dm_report.iq_tones->i_remote[i] =0;
        dm_report.iq_tones->q_remote[i] =0;
        }
        for(int i=0;i<80;i++){
        dm_report.tone_sinr_indicators.sinr_indicator_local[i] =0;
        dm_report.tone_sinr_indicators.sinr_indicator_remote[i] =0;
        }

        // Execute measurement
        nrf_dm_status_t status = nrf_dm_configure(&dm_config);
        debug_start();
        uint32_t timeout_us = 0.5e6;
        status     = nrf_dm_proc_execute(timeout_us);
        debug_stop();

        float distance = 0;
        uint32_t duration = 0;
        uint8_t hopping_sequence[NRF_DM_CHANNEL_MAP_LEN];

        if(status == NRF_DM_STATUS_SUCCESS){
            nrf_dm_populate_report(&dm_report);
            nrf_dm_quality_t quality = nrf_dm_calc(&dm_report);
            duration = nrf_dm_get_duration_us(&dm_config);
            distance = nrf_dm_high_precision_calc(&dm_report);
            nrf_dm_get_hopping_sequence(&dm_config,hopping_sequence);

        } else{  // Failure
       
        dm_report.quality = 100;
        debug_pulse(10);
        }

        //Send report to UART
        uart_init();
        nrf_dm_report_to_json(&dm_report,distance,duration,hopping_sequence);
        uart_uninit();


        // Check for role change after each execution
        MeasPair new_result = read_uart_role();
        int new_role = new_result.role;
        int new_seed = new_result.seed;
        if (new_role != CMD_UNKNOWN) {
            return new_result; 
        }
    }
}


MeasPair run_reflector(int seed){
    static nrf_dm_config_t dm_config;

    dm_config = NRF_DM_DEFAULT_CONFIG;
    dm_config.role = NRF_DM_ROLE_REFLECTOR;
    dm_config.rng_seed = seed;


    while(1){
        nrf_dm_status_t status = nrf_dm_configure(&dm_config);
        debug_start();
        uint32_t timeout_us = 3e6;
        status = nrf_dm_proc_execute(timeout_us);
        debug_stop();

        if (status == NRF_DM_STATUS_SUCCESS){
            debug_pulse(10);
        } else {
            debug_pulse(5);
        }

        // Check for role change after each execution
        MeasPair new_result = read_uart_role();
        int new_role = new_result.role;
        int new_seed = new_result.seed;
        if (new_role != CMD_UNKNOWN) {
            return new_result; 
        }
    }
}

MeasPair run_none(int seed){
    static nrf_dm_config_t dm_config;

    dm_config = NRF_DM_DEFAULT_CONFIG;
    dm_config.role = NRF_DM_ROLE_REFLECTOR;
    dm_config.rng_seed = seed;

    nrf_dm_status_t status = nrf_dm_configure(&dm_config);
    while(1){
        // Check for role change after each execution
        MeasPair new_result = read_uart_role();
        int new_role = new_result.role;
        int new_seed = new_result.seed;
        if (new_role != CMD_UNKNOWN) {
            return new_result; 
        }
    }

}