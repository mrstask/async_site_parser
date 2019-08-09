import os


def create_directory(domain):
    directory = os.getcwd() + '/'
    if not os.path.exists(directory + domain + '/'):
        os.mkdir(directory + domain)
