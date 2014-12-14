# Sort Images

This is a script I wrote to organize folders with tons of unorganized, unclassified and untagged images. In my case what I had in mind was [Dropbox’s Camera Uploads](https://www.dropbox.com/en/help/289) folder, for example.

This script reads all image files under a specified folder ad sort the images in folders and subfolders according to three criteria:

* `origin` of the image (that is, the device or software that created the file)
* `date` of the image (that is, when it was created)
* `size` of the image (that is, its width and height in pixels)

It organized my 5Gb _Camera Uploads_ folders in 14 seconds.


This script was inspired by [Henrique Bastos’s tweet](https://twitter.com/henriquebastos/status/540823845477703680) about [Vladimir Keleshev's presentation](http://youtu.be/pXhcPJK5cMc). When I saw it I got eager to try [Docopt](https://github.com/docopt/docopt).

## Requirements

* Python 2.7.
* [virtualenv](https://virtualenv.pypa.io/) and [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/) are not required, but are recommended.
* [pip](https://github.com/pypa/pip) is not required, but I’m using it in install instructions – if you want to install it, download [get-pip.py](https://bootstrap.pypa.io/get-pip.py) and run this command on your download folder `$ python get-pip.py`.


# Install

Clone the repository:

```
$ git clone git@github.com:cuducos/sortimages.git
```

Go to the repository folder:

```
$ cd sort images
```

Install the packages needed to run the script:

```
$ pip install -r requirements.txt
```

Get usage instructions:

```
$ python sortimages.py -h
```


## Usage

```
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
```

### Basic usage

This command organizes images under a given folder (`/User/johndoe/Image Folder`) creating sub folders according to the device (or application) that created the image:

```
$ python sortimages.py origin '/Users/johndoe/Image Folder'
```

* Quotes were necessary as the path had a space;
* Relative paths are accepted;
* Using `~` as an alias to home folder will not work (but pull requests are welcomed).

The output gives you details about the process:

```
==> Reading /Users/johndoe/Test Folder
    [33%] Reading /Users/johndoe/Test Folder/2012-04-26 13.56.26.png
    [67%] Reading /Users/johndoe/Test Folder/2014-12-06 15.07.32.jpg
    [100%] Reading /Users/johndoe/Test Folder/2014-12-06 17.11.27-1.jpg

==> Sorting 3 images
    [33%] /Users/johndoe/Test Folder/2012-04-26 13.56.26.png => /Users/johndoe/Test Folder/Undefined Origin/2012-04-26 13.56.26.png
    [67%] /Users/johndoe/Test Folder/2014-12-06 15.07.32.jpg => /Users/johndoe/Test Folder/iPhone 4S - 8.1.1/2014-12-06 15.07.32.jpg
    [100%] /Users/johndoe/Test Folder/2014-12-06 17.11.27-1.jpg => /Users/johndoe/Test Folder/iPhone 4S - Instagram/2014-12-06 17.11.27-1.jpg

==> Summary: 3 images sorted in a moment
    1 images moved to /Users/johndoe/Test Folder/iPhone 4S - Instagram
    1 images moved to /Users/johndoe/Test Folder/iPhone 4S - 8.1.1
    1 images moved to /Users/johndoe/Test Folder/Undefined Origin
```

### Sub sorting

You can combine more than one sorting criteria, for example:

```
$ python sortimages.py date '/Users/johndoe/Test Folder' --size
```

This command uses `date` as the main criterion, but sub sorts the image according to their `size` (this happens inside the folders created by `date`):

```
==> Reading /Users/johndoe/Test Folder
    [33%] Reading /Users/johndoe/Test Folder/2012-03-26 07.56.11.jpg
    [67%] Reading /Users/johndoe/Test Folder/2012-03-26 12.22.27.jpg
    [100%] Reading /Users/johndoe/Test Folder/2012-03-26 19.11.30.jpg

==> Sorting 3 images
    [33%] /Users/johndoe/Test Folder/2012-03-26 07.56.11.jpg => /Users/johndoe/Test Folder/2012/3/26/1648x432/2012-03-26 07.56.11.jpg
    [67%] /Users/johndoe/Test Folder/2012-03-26 12.22.27.jpg => /Users/johndoe/Test Folder/2012/3/26/960x1280/2012-03-26 12.22.27.jpg
    [100%] /Users/johndoe/Test Folder/2012-03-26 19.11.30.jpg => /Users/johndoe/Test Folder/2012/3/26/480x640/2012-03-26 19.11.30.jpg

==> Summary: 3 images sorted in a moment
    1 images moved to /Users/johndoe/Test Folder/2012/3/26/960x1280
    1 images moved to /Users/johndoe/Test Folder/2012/3/26/1648x432
    1 images moved to /Users/johndoe/Test Folder/2012/3/26/480x640
```

Available options are (you can combine them, for example using `-o -s` for `origin` and `size`):

* `-d` or `--date` to sort the resulting folders by date
* `-o` or `--origin` to sort the resulting folders by origin
* `-s` or `--size`to sort the resulting folders by image size in pixels

### Recursive

If the folder you want to scan has sub-folders, you can user `-r` or `--recursive`:

```
$ python sortimages.py size '/Users/johndoe/Test Folder' -o -r
```

This command look for all images in the given folder, including it sub-folders (after sorting the images, any empty directory will be deleted):
 
```
==> Reading /Users/johndoe/Test Folder
    [33%] Reading /Users/johndoe/Test Folder/2012-03-27 12.22.27.jpg
    [67%] Reading /Users/johndoe/Test Folder/sub-folder/2012-03-29 09.11.30.jpg
    [100%] Reading /Users/johndoe/Test Folder/sub-folder/sub-sub-folder/2012-03-26 17.56.11.jpg

==> Sorting 3 images
    [33%] /Users/johndoe/Test Folder/2012-03-27 12.22.27.jpg => /Users/johndoe/Test Folder/960x1280/Undefined Origin/2012-03-27 12.22.27.jpg
    [67%] /Users/johndoe/Test Folder/sub-folder/2012-03-29 09.11.30.jpg => /Users/johndoe/Test Folder/480x640/iPhone 4S - 5.1/2012-03-29 09.11.30.jpg
    [100%] /Users/johndoe/Test Folder/sub-folder/sub-sub-folder/2012-03-26 17.56.11.jpg => /Users/johndoe/Test Folder/1648x432/Undefined Origin/2012-03-26 17.56.11.jpg

==> Summary: 3 images sorted in a moment
    1 images moved to /Users/johndoe/Test Folder/960x1280/Undefined Origin
    1 images moved to /Users/johndoe/Test Folder/1648x432/Undefined Origin
    1 images moved to /Users/johndoe/Test Folder/480x640/iPhone 4S - 5.1
```

## Contribute

* Fork this reposiotry
* Create a new branch: `git checkout -b awesome-feature`
* Commit your changes: `git add -A . && commit -m 'Add awesome feature'`
* Push to the branch: `git push origin awesome-feature`
* And create a pull request.

## License

Copyright (c) 2014 Eduardo Cuducos.

Licensed under the [MIT License](http://opensource.org/licenses/MIT).