# FPGA Connection Speed Tester
Or FCST for short. Application for testing connection with FPGA device through ethernet and UDP packets. It measures speed of raw data sent by 
FPGA. Connection parameters like ip addresses, ports and setup datagrams are configured through json file. 

###How to use FCST
1. Create json configuration file. How to do it is described in section above - JSON configuration file.
2. Run fcst_console_ui.py with config file name as command line parameter.

###JSON configuration file
Configuration file is in form of dictionary, which contains following elements:
- fcst_ip: string
- fcst_port_in: int
- fcst_port_out: int
- fpga_ip: string
- start_datagram: datagram_t
- setup_datagrams: list of datagram_t

datagram_t is dictionary that contains following elements:
- fpga_port: int
- data_hex: string OR data_dec: string OR data_bin: string


####fcst_ip
This string contains IP address for FCST application.

####fcst_port_in
This int contains port on which FCST application will listen for test datagrams from FPGA.

####fcst_port_out
This int contains port from which FCST application will send setup datagrams to FPGA.

####fpga_ip
This string contains IP address that FPGA has.

####start_datagram
This element contains info about start datagram. When FPGA receives start datagram it begins sending test datagrams and 
test starts.

####setup_datagrams
This list contains info about datagrams that will be sent before starting the test.

####Example
config.json
```json
{
    "fcst_ip": "127.0.0.12",
    "fcst_port_in": 12666,
    "fcst_port_out": 12666,
    "fpga_ip": "127.0.0.11",
    "start_datagram": {
        "fpga_port": 12666,
        "data_hex": "0x180"
    },
    "setup_datagrams": [
        {
            "fpga_port": 14666,
            "data_dec": "1400"
        },
        {
            "fpga_port": 15666,
            "data_bin": "100000"
        }
    ]
}
```

###Project Structure
Project consists of one folder and two files:
- fcst folder
- fcst_console_ui.py
- fpga_mockup.py

####fcst folder
It contains all modules for FCST. main.py contains all methods needed for performing whole test, but it does not 
provide any user interface.

####fcst_console_ui.py
Provides user interface for main.py.

####fpga_mockup.py
Substitution for real FPGA. It imitates its responses.