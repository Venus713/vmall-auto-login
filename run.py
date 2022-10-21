import argparse

from src.scrapers import Hktvmall

parser = argparse.ArgumentParser()


if __name__ == '__main__':
    parser.add_argument('-n', '--name', help='scraper name', default='htkvmall')
    args = parser.parse_args()

    hktvmall = Hktvmall()
    hktvmall.main()
