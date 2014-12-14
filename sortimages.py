# coding: utf-8

"""
Sort images.

Usage:
  sortimages.py origin (<directory>) [-r|--recursive] [-o|--origin] [-d|--date] [-s|--size]
  sortimages.py date (<directory>) [-r|--recursive] [-o|--origin] [-d|--date] [-s|--size]
  sortimages.py size (<directory>) [-r|--recursive] [-o|--origin] [-d|--date] [-s|--size]
  sortimages.py (-h | --help)
  sortimages.py (-v | --version)

Commands:
  origin       Sort the images by origin - camera, device or software
  date         Sort the images by date of creation
  size         Sore the images by size - width and height in pixels

Arguments:
  directory The path to the directory to be scanned

Options:
  -d --date         Sort the resulting directories by date
  -h --help         Show this helper instructions
  -o --origin       Sort the resulting directories by origin
  -r --recursive    Recursive, scan sub-directories too
  -s --size         Sort the resulting directories by image size in pixels
  -v --version      Show the version of this software

"""
from datetime import datetime
from dimensions import dimensions
from docopt import docopt
from exifread import process_file
from humanize import naturaldelta
from mimetypes import guess_type
from operator import itemgetter
from re import compile
from sys import exit
from time import localtime, strftime
from unipath import FILES, DIRS, Path


class SortImages(object):

    # Main methods (init & run)

    def __init__(self, docopt_arguments=None):

        # support vars
        self.started_at = datetime.now()
        self.arguments = self.__rename_option_keys(docopt_arguments)
        self.sorting_possibilities = ['date', 'origin', 'size']

        # main vars
        self.sort = self.__get_main_sort()
        self.sub_sorts = self.__get_sub_sorts()
        self.recursive = self.arguments['options']['recursive']
        self.directory = self.__check_directory()
        self.original_directory = self.directory

    def run(self):

        # support vars
        sort_map = self.__get_images()
        count = 1
        total = len(sort_map)
        tags = dict()

        # loop through image list
        self.__output('Sorting {} images'.format(total))
        for image in sort_map:

            # get target
            tag = image['tag']
            target = self.__get_child(tag)

            # output
            msg = '[{}] {} => {}'.format(self.__percent(count, total),
                                         image['path'],
                                         target.child(image['path'].name))
            self.__output(msg, header=False)

            # move and save stats
            image['path'].move(target.child(image['path'].name))
            count += 1
            tags[tag] = tags.get(tag, 0) + 1

        # summary
        timer = naturaldelta(datetime.now() - self.started_at)
        msg = 'Summary: {} images sorted in {}'.format(total, timer)
        self.__output(msg)
        summary = list()
        for tag, count in reversed(sorted(tags.items(), key=itemgetter(1))):
            target = self.__get_child(tag)
            summary.append('{} images moved to {}'.format(count, target))
        self.__output(summary + [''], header=False)
        self.__clean_empty_dirs()

    # Helper methods supporting __init__():

    @staticmethod
    def __rename_option_keys(arguments):
        """
        Group from options values (`--help`) in a sub dictionary for options.
        :param arguments: (dict) arguments from docopt
        :return: (dict) inputted arguments with no keys for individual options,
        and an extra element which is a dictionary holding options without the
        `--` in the key name
        """
        options = dict()
        for key in arguments.keys():
            if key[0:2] == '--' and key not in ('--help', '--version'):
                new_key = key[2:].replace('-', '_')
                options[new_key] = arguments[key]
                del(arguments[key])
        arguments['options'] = options
        return arguments

    def __get_main_sort(self):
        """
        Returned the main sort criterion.
        :return: (str) date, origin or size
        """
        for sort in self.sorting_possibilities:
            if self.arguments[sort]:
                return sort

    def __get_sub_sorts(self):
        """
        Returned the list of options for sub sorts.
        :return: (list of str or None) date, origin, size and/or recursive
        """
        options = list()
        for option in self.sorting_possibilities:
            if self.arguments['options'][option]:
                options.append(option)
        count = len(options)
        if count == 0:
            return None
        else:
            return options

    def __check_directory(self):
        """
        Check if the entered directory exists
        :return: (unipath.Path or False) the path to the existing directory
        """
        directory = Path(self.arguments['<directory>'])
        if not directory.exists() or not directory.isdir():
            msg = '{} is not a valid directory'.format(directory.absolute())
            self.__output(msg, error=True)
            return False
        return directory

    # Helper methods supporting run():

    def __get_images(self):
        """
        Return a list of all the image files inside the directory
        :return: (list of unipath.Path) list of files
        """
        images = list()
        files = self.__ls()
        files_total = len(files)
        file_count = 0
        self.__output('Reading {}'.format(self.directory.absolute()))
        for file_name in files:

            # print reading status
            file_count += 1
            percent = self.__percent(file_count, files_total)
            msg = '[{}] Reading {}'.format(percent, file_name.absolute())
            self.__output(msg, header=False)

            # sort
            if self.__is_image(file_name.absolute()):
                tag = self.__get_image_tag(file_name)
                images.append({'tag': tag, 'path': file_name})

        return images

    def __get_image_tag(self, image):
        """
        Get a path to a image file and return the tags to sort this image
        :param image: (str or unipath.Path) path to an image file
        :return: (tuple) with the tags to sort the image
        """

        # load sorting methods
        criteria = [self.sort]
        if self.sub_sorts:
            criteria.extend(self.sub_sorts)
        full_tags = list()

        # find all tags
        for criterion in criteria:

            # method for size
            if criterion == 'size':
                image_properties = dimensions(str(image))
                tag = '{}x{}'.format(image_properties[0], image_properties[1])
                full_tags.append(self.__image_tag(tag))

            # method for date
            if criterion == 'date':

                # set possible date exif keys
                keys = ['Image DateTime',
                        'EXIF DateTimeDigitized',
                        'GPS GPSDate']

                # fetch the key values
                with open(image, 'r') as file_handler:
                    exif = process_file(file_handler)
                    for key in keys:
                        tag = exif.get(key, False)
                        if tag:
                            break
                    if not tag:
                        file_path = Path(image)
                        tag = strftime('%Y:%m:%d', localtime(file_path.ctime()))

                # create sub tags
                tag = str(tag)
                if tag != 'Undefined Date':
                    if len(tag.strip()) > 10:
                        date_tag = datetime.strptime(tag, '%Y:%m:%d %H:%M:%S')
                    else:
                        date_tag = datetime.strptime(tag, '%Y:%m:%d')
                    for sub_tag in ['%Y', '%m', '%d']:
                        formatted = date_tag.strftime(sub_tag)
                        full_tags.append(self.__image_tag(formatted, True))
                else:
                    full_tags.append(self.__image_tag(tag))

            # method for origin
            if criterion == 'origin':

                # fetch the key values
                with open(image, 'r') as file_handler:

                    # get info
                    exif = process_file(file_handler)
                    model = exif.get('Image Model', False)
                    software = exif.get('Image Software', False)
                    make = exif.get('Image Make', False)

                    # if software is just a version number, skip it
                    regex = compile('[^a-zA-Z]+')
                    test = str(software)
                    if len(regex.sub('', test.replace('Camera', ''))) == 0:
                        software = False

                    # generate tag
                    if model and software:
                        tag = '{} - {}'.format(model, software)
                    elif model:
                        tag = str(model)
                    elif software:
                        tag = str(software)
                    elif make:
                        tag = str(make)
                    else:
                        tag = 'Undefined Origin'

                # append tag
                full_tags.append(self.__image_tag(tag))

        return tuple(full_tags)

    def __ls(self):
        if self.recursive:
            files = [f for f in self.directory.walk(filter=FILES)]
        else:
            files = self.directory.listdir(filter=FILES)
        return files

    @staticmethod
    def __is_image(path):
        """
        Gets the path to an image and test if the file is actually an image
        :param path: (str or uniptah.Path) path to an image
        :return: (boolean) True if the file is a image, else False
        """
        allow = ['image/' + t for t in ['png', 'gif', 'jpeg', 'jpeg', 'tiff']]
        if guess_type(path)[0] in allow:
            return True

    @staticmethod
    def __image_tag(string, number=False):
        """
        Formats the tag to avoid special chars in directory creations
        :param string: (str) the original tag
        :param number: (boolean) if number, converts to int to remove leading 0
        :return: (str) the formatted tag without special chars
        """
        regex = compile('[^a-zA-Z0-9._ ]+')
        tag = regex.sub('-', string.strip())
        if number:
            return str(int(tag))
        return tag

    def __get_child(self, tags):
        target = self.directory
        for tag in tags:
            target = target.child(tag)
            if not target.exists():
                target.mkdir()
        return target

    def __clean_empty_dirs(self):
        """
        Delete empty directories
        :return: (None)
        """

        # clean os garbage
        garbage_list = ['.DS_Store',
                        '.DS_Store?',
                        '.Spotlight-V100',
                        '.Trashes',
                        'ehthumbs.db',
                        'Thumbs.db']
        files = [d for d in self.directory.walk(filter=FILES)]
        for file_path in files:
            if file_path.name in garbage_list:
                file_path.remove()

        # delete empty directories
        directories = [d for d in self.directory.walk(filter=DIRS)]
        for directory in directories:
            files = directory.listdir()
            if len(files) == 0:
                directory.rmdir(parents=True)

    # Helper function for outputs

    @staticmethod
    def __output(msg, **kwargs):
        """
        Prints a message in the terminal
        :param msg: (str or list) the message to be printed (use list for multi-
        line)
        :param kwargs: if error=False, exit the program after printing the
        message; if header=True prints an arrow ('==> ') before the message, if
        header=False, prints 4 spaces ('    ') before the message.
        :return: (None)
        """
        error = kwargs.get('error', False)
        header = kwargs.get('header', True)
        prefix = '\n==> ' if header else '    '
        if isinstance(msg, list):
            output = '\n'.join([prefix + line for line in msg])
        else:
            output = prefix + msg
        print output
        if error:
            print ' '
            exit()
        return None

    @staticmethod
    def __percent(number, total):
        """
        Format a percentage without decimals
        :param number: (int or float) the partial
        :param total: (int or float) the total
        :return: (str) percentage formatted (eg. 25% for 1/4)
        """
        number = float(number)
        return '{0:.0f}%'.format((number * 100) / total)

# run

if __name__ == '__main__':
    run_forrest = SortImages(docopt(__doc__, version='Sort Images 0.0.1'))
    run_forrest.run()
