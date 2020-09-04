import argparse

from fcst.manager import *


def start_test():
    try:
        print("Starting test...")
        manager.start_test()
    except IncompleteSetup:
        print("[error] Cannot start test. Setup is incomplete.")


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
    except NotProperlyConfigured:
        print('Error occurred while loading configuration. Setup incomplete.')


if __name__ == '__main__':
    args = parse_arguments()

    manager = Manager()
    load_setup()
    manager.prepare_socket()  # todo remove
    manager.send_setup_to_fpga()

    start_test()
