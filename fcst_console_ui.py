import argparse

from fcst.manager import *


def start_test(man):
    try:
        print("Starting test...")
        man.start_test()
    except IncompleteSetup:
        print("[error] Cannot start test. Setup is incomplete.")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str,
                        help="name of json file")
    arguments = parser.parse_args()
    return arguments


if __name__ == '__main__':
    args = parse_arguments()

    manager = Manager(args.filename)
    manager.send_setup_to_fpga()

    start_test(manager)

