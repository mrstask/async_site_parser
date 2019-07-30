import argparse

my_parser = argparse.ArgumentParser()

my_parser.add_argument('url', action='store')
my_parser.add_argument('-silent', action='store_true')

args = my_parser.parse_args()

# print(args.input)
# print(args.first)
# print(args.others)
print(args.url)
if args.silent:
    print('Silent')