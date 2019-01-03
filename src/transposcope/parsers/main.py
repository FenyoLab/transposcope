import argparse


def main():
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parse TIPseqHunter or MELT output for visualization")
    # TODO read some other parsers help for pointers
    parser.add_argument('-s', '--source', help='The path to the source file')
    parser.add_argument('-f', '--format', help='The input type [MELT, TIPseqHunter]')
    args = parser.parse_args()
