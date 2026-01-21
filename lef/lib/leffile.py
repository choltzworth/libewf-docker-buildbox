import json
import os
import shutil
import pyewf # pyewf is python bindings for libewf: https://github.com/libyal/libewf/wiki/Python-development
import glob
import re

class LefFile:
    """
    The LefFile class represents a LEF archive, and provides functionality to
    list and extract all contents.
    """

    """ Number of files per. directory when extracting in sequential numbering mode (-n) """
    NUMBERING_FILES_PR_DIRECTORY = 100000000
    """ Format used for directory and filename when extracting in sequential numbering mode (-n) """
    NUMBERING_FILENAME_FORMAT = "08d"
    """ Magic bytes used to identify AppleDouble files
    (from https://tools.ietf.org/html/rfc1740) """
    APPLE_DOUBLE_MAGIC_BYTES = b'\x00\x05\x16\x07'
    """ Default filename to use if a file entry does not have a filename set """
    DEFAULT_FILE_NAME = "[NO NAME]"

    def __init__(self, filename, suppress_apple_double_files=False):
        """
        Initializes a new 'LefFile' object.

        :param filename: Filename of LEF file to work on.
        :param suppress_apple_double_files: Supress Apple Double files when listing and extracting.
        :return: returns nothing
        """
        self.filename = filename
        self.ewffile = None
        self.file_number = 0
        self.numbering_mode = False
        self.suppress_apple_double_files = suppress_apple_double_files

    def validate_filetype(self):
        """ Validates the filename supplied in initialize is a LEF or EWF file. """
        return pyewf.check_file_signature(self.filename)

    def list_file_contents(self):
        """ Lists file contents in JSON format to stdout. """
        self.open_file()
        root_file = self.ewffile.get_root_file_entry()
        self.print_file_info_resursively(root_file)
        self.close_file()

    def print_file_info_resursively(self, input_file, path=""):
        """ Prints file information for input_file and all children resursively. """
        if not self.suppressed_file(input_file):
            self.print_file_info(input_file, path)
        subentries = input_file.get_number_of_sub_file_entries()
        current_path = os.path.join(path, self.get_name_safe(input_file))
        for i in range(subentries):
            subfile = input_file.get_sub_file_entry(i)
            self.print_file_info_resursively(subfile, current_path)

    def print_file_info(self, input_file, path):
        """ Prints file information for input_file in JSON to stdout. """
        file_information = {
            'name': os.path.join(path, self.get_name_safe(input_file)),
            'create': str(input_file.get_creation_time()),
            'modify': str(input_file.get_modification_time()),
            'access': str(input_file.get_access_time()),
            'size': input_file.get_size(),
            'directory': self.is_directory(input_file)
        }
        if self.numbering_mode:
            file_information['extracted_name'] = self.get_output_path(input_file, path)

        print(json.dumps(file_information))

    # Methods for extracting content
    def extract_file(self, ewf_file, path, target_directory):
        """ Extracts ewf_file to target_directory under path provided. """
        output_path = self.get_output_path(ewf_file, path)
        output_filename = os.path.join(target_directory, output_path)

        # Check if output file is a directory
        if self.is_directory(ewf_file):
            # If a directory and in numbering mode - ignore it
            if self.numbering_mode:
                return
            # else create directory
            if not os.path.exists(output_filename):
                os.makedirs(output_filename)
        else:
            # If its a file copy the file to output directory
            self.copy_file(ewf_file, output_filename)

        self.print_file_info(ewf_file, path)
        self.increment_file_number()


    def extract_file_resursively(self, ewf_file, path, target_directory):
        """ Extracts ewf_file and all children to target_directory under path provided. """
        if not self.suppressed_file(ewf_file):
            self.extract_file(ewf_file, path, target_directory)
        subentries = ewf_file.get_number_of_sub_file_entries()

        if subentries > 0:
            current_path = os.path.join(path, self.get_name_safe(ewf_file))
            for i in range(subentries):
                sub_ewf_file = ewf_file.get_sub_file_entry(i)
                self.extract_file_resursively(sub_ewf_file, current_path, target_directory)

    def extract_to_directory(self, target_directory, numbering=False):
        """ Extract all files in LefFile to target_directory. """
        self.numbering_mode = numbering
        self.open_file()
        root_file = self.ewffile.get_root_file_entry()
        self.extract_file_resursively(root_file, "", target_directory)
        self.close_file()

    def copy_file(self, ewf_file, output_filename):
        """ Helper to copy a ewf_file object to a filename ensuring missing dirs gets created """
        # Ensure path exists
        dirname = os.path.dirname(output_filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        # Copy file
        output_file = open(output_filename, 'wb')
        shutil.copyfileobj(ewf_file, output_file)
        output_file.close()

    # Numbering helper
    def get_output_path(self, ewf_file, path):
        """ Returns the output path for the file given the current extract mode """
        if self.numbering_mode:
            # If numbering mode calculate the directory and file number
            directory_number = self.file_number // self.NUMBERING_FILES_PR_DIRECTORY
            filename_number = self.file_number % self.NUMBERING_FILES_PR_DIRECTORY
            directory_name = format(directory_number, self.NUMBERING_FILENAME_FORMAT)
            (_, extension) = os.path.splitext(self.get_name_safe(ewf_file))
            filename = format(filename_number, self.NUMBERING_FILENAME_FORMAT) + extension
            return os.path.join(directory_name, filename)
        # Else just combine the filename with the path
        return os.path.join(path, self.get_name_safe(ewf_file))

    def increment_file_number(self):
        """ Increments number of files extracted """
        self.file_number += 1

    def open_file(self):
        """ Helper to open LefFile. """
        # Open file and return pyewf handle
        self.ewffile = pyewf.open(self.glob_filename())

    def close_file(self):
        """ Close LefFile after use. """
        self.ewffile.close()

    def glob_filename(self):
        """ Globs the filename to find accompanying segment files for multi-part files.  """
        basename, extension = os.path.splitext(self.filename)
        extracted_extension_match = re.match(r'\.[lL][xX]{0,1}', extension)
        if extracted_extension_match is None:
            return [self.filename]
        extracted_extension = extracted_extension_match.group(0)
        filenames = glob.glob("{0}{1}*".format(basename, extracted_extension))
        filenames.reverse()
        return filenames

    # File Helpers
    def is_directory(self, file):
        """ Returns true if ewffile is a directory. """
        # Check if get_file_type is available in pywef library
        if hasattr(file, 'get_file_type') and callable(file.get_file_type):
            # Use file type function
            file_type = file.get_file_type()
            # File type is either ord('f') for file or ord('d') for directory
            return file_type == ord('d')
        # else: Use naive method
        # This is slower and not bulletproof, but best effort without file_type.
        # Check if it has subentries, if so its a dir.
        if file.get_number_of_sub_file_entries() > 0:
            return True
        # else: It still could be an empty directory
        try:
            # If we can read from file, it is not a directory
            file.read(1)
            file.seek(0)
            return False
        except OSError:
            # If reading throws an exception its likely a directory
            return True

    def get_name_safe(self, file):
        """ Returns file name or DEFAULT_FILE_NAME if no filename is set. """
        return file.get_name() if file.get_name() is not None else self.DEFAULT_FILE_NAME

    def suppressed_file(self, file):
        """ Returns true if --suppress-apple-double-files switch is enabled,
        and file is AppleDouble file """
        if (self.suppress_apple_double_files
                and not self.is_directory(file)
                and file.get_size() > 4):
            magic_bytes = file.read(4)
            file.seek(0)
            if magic_bytes == self.APPLE_DOUBLE_MAGIC_BYTES:
                return True
            return False
        return False
