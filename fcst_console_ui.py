import argparse

from fcst.manager import Manager

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str,
                        help="name of json file")
    args = parser.parse_args()
    fcst = Manager(args.filename)
    fcst.send_setup_to_fpga()
    fcst.start_test()
