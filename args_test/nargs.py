import argparse

my_parser = argparse.ArgumentParser()
# my_parser.add_argument('input',
#                        action='store',
#                        nargs='?',
#                        default='my default value')

my_parser.add_argument('input',
                       action='store',
                       nargs='*',
                       default='my default value')
my_parser.add_argument('first', action='store')
my_parser.add_argument('others', action='store', nargs=argparse.REMAINDER)

args = my_parser.parse_args()

print(args.input)
print(args.first)
print(args.others)