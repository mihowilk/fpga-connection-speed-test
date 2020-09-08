import argparse
from datetime import datetime
import sys
import logging

from fcst.manager import *
from exceptions import *


def start_test():
    try:
        print("Starting test...")
        manager.start_test()
    except IncompleteSetup:
        print("[error] Cannot start test. Setup is incomplete.")
        exit(1)


def setup_logger():
    result_filename = f"results/results_{datetime.today().strftime('%Y-%m-%d-%H:%M:%S')}.log"

    logger = logging.getLogger("speed_test_logger")
    logger.setLevel(logging.DEBUG)
    log_formatter = logging.Formatter("%(asctime)s "
                                      "[%(levelname)s] %(message)s")

    file_handler = logging.FileHandler(result_filename, mode="w")
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)

    return logger


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str,
                        help="name of json file")
    arguments = parser.parse_args()
    return arguments


def load_setup():
    try:
        manager.load_setup(args.filename)
        print("Setup complete")
    except GeneralSetupError:
        print('[Error] Wrong general connection parameters (like ip addreses and ports) given in config file. Setup '
              'incomplete.')
        exit(1)
    except SetupDatagramError:
        print('[Error] Wrong or none setup datagram list given in config file. Setup incomplete.')
        exit(1)
    except StartDatagramError:
        print('[Error] Wrong or none start datagram is given in config file. Setup incomplete.')
        exit(1)


if __name__ == '__main__':
    args = parse_arguments()

    manager = Manager()
    setup_logger()
    load_setup()
    manager.send_setup_to_fpga()

    start_test()
