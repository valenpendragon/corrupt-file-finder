import zipfile
import pypdf
import sys
import os
import glob
import pathlib


def check_pdf(filepath):
    """This function requires a filepath to a file to be tested.
    It returns a tuple (bool, exception or None). The function returns
    (True, None) for uncorrupted PDFs, False and the actual Exception
    generated or 'Bad Metadata' if the file is corrupt.
    :param: filepath: str of a filepath
    :return: tuple (bool, None/Exception/Bad Metadata) """
    print(f"Testing PDF file {filepath}")
    with open(filepath, 'rb') as fp:
        try:
            pdf = pypdf.PdfReader(fp)
            info = pdf.metadata
            if info is not None:
                result = (True, None)
            else:
                result = (False, "Bad Metadata")
            return result
        except Exception as e:
            # print(f"Opening PDF, {filepath}, produced Exception: {e}")
            result = (False, e)
            return result


def check_zip(filepath):
    """This function requires a filepath to a file to be tested.
    It returns a tuple (bool, exception or None). The function returns
    (True, None) for uncorrupted zip files, False and the actual Exception
    generated or the name of a corrupted file inside the zip file.
    :param: filepath: str of a filepath
    :return: tuple (bool, None/Exception/filename) """
    print(f"Testing zip file {filepath}")
    with open(filepath, 'rb') as fp:
        try:
            zip_file = zipfile.ZipFile(filepath)
            ret = zip_file.testzip()
            if ret is not None:
                # print(f"The first bad file in {filepath} is {ret}")
                result = (False, {ret})
            else:
                result = (True, None)
            return result
        except Exception as e:
            # print(f"Opening zip file, {filepath}, produced Exception: {e}")
            result = (False, e)
            return result


def get_files_from_target_dir(target_dir, file_types, recurse=False) -> list:
    """
    This function requires a filepath and list of filetypes as strings of suffixes.
    :param target_dir: filepath
    :param file_types: list of str, e.g. 'pdf', 'zip'
    :return: list of filepaths
    """
    file_list = []
    for file_type in file_types:
        if recurse:
            search_str = f"{target_dir}/**/*.{file_type}"
            file_list.extend(glob.glob(search_str, recursive=True))
        else:
            search_str = f"{target_dir}/*.{file_type}"
            file_list.extend(glob.glob(search_str))
    return file_list


def write_report_to_disk(report_file, results):
    """
    This function requires a list of tuples in the form (filepath, bool, error) where
    filepath is the path to the file testes; bool is True if the file is not corrupt,
    False if corrupt; and error is None for files that are not corrupt or a str containing
    the first major error encountered while testing the file. These tuples are used to
    write the report to disk in the same fashion as it was written to stdout. Using this
    option will not suppress the messages indicating the file currently being tested, but
    it will suppress the final report. It returns True if the report write was successful,
    False otherwise. The format of the file is CSV with delimiter semi-colon.
    :param report_file: filepath
    :param results: list of tuples (filepath, bool, error|None)
    :return: bool, True if the file write occurred without errors, False otherwise
    """
    try:
        with open(report_file, "w") as fp:
            fp.write(f"Filepath;Usable?;Known Errors\n")
            for file, result, error_msg in results:
                if result:
                    fp.write(f"{file};usable;No errors found\n")
                else:
                    fp.write(f"{file};corrupted;{error_msg}\n")
    except OSError:
        return False
    return True


if __name__ == "__main__":
    """This program has the following exit codes:
    1: invalid command line usage
    2: target directory does not exist or is not a directory
    3: target directory is not readable
    4: report file creation failed
    """
    args = sys.argv
    len_args = len(args)
    valid_arguments = ['-p', '--pdf', '-z', '--zip', '-r', '--recurse', '--report-file']
    # print(f"args: {args}")

    help_txt = f"Usage: main.py [-p|--pdf] [-z|--zip] [-r|--recurse] [--report-file filepath] directory\n" \
               f"Note: report file arguments must appear after file type arguments."

    if len_args == 1:
        print(f"corrupt_file_finder: At least one file types and the name of the target directory must be specified.")
        print(f"{help_txt}")
        exit(1)
    elif len_args == 2:
        print(f"corrupt_file_finder: At least one file types must be specified in the arguments")
        print(f"{help_txt}")
        exit(1)
    elif args[-1] in valid_arguments:
        print(f"corrupt_file_finder: A target directory must be specified.")
        print(f"{help_txt}")
        exit(1)

    if '--report-file' in args:
        if args[-3] != '--report-file':
            print(f"corrupt_file_finder: report-file argument must appear after file type arguments.")
            print(f"{help_txt}")
            exit(1)
        elif args[-3] == '--report-file' and args[-2] in valid_arguments:
            print(f"corrupt_file_finder: A filepath for the report file must be specified after the argument.")
            print(f"{help_txt}")
            exit(1)
        elif args[-2] == '--report-file':
            print(f"corrupt_file_finder: A filepath for the report file must be specified after the argument.")
            print(f"{help_txt}")
            exit(1)

    # Identify target directory and remove it from arguments.
    # Removing any extraneous double quotation marks that might carry over
    # to the actual string stored in target_dir.
    target_dir = args[-1].replace('"', '')
    args.pop(-1)
    # print(f"target_dir: {target_dir}")

    # Setting up file types to examine and default flags.
    file_types = []
    recurse = False
    write_report = False

    # Checking for report-file arguments. They will be at -2 and -1.
    if args[-2] == '--report-file':
        report_file = args.pop(-1)
        # Remove the report-file argument, which is now at -1.
        args.pop(-1)
        write_report = True
        # print(f"report_file: {report_file}. write_report: {write_report}")
        # print(f"args: {args}")

    for idx, arg in enumerate(args):
        match arg:
            case 'main.py':
                continue
            case '-p':
                file_types.append('pdf')
            case '--pdf':
                file_types.append('pdf')
            case '-z':
                file_types.append('zip')
            case '--zip':
                file_types.append('zip')
            case '-r'| '--recurse':
                recurse = True
            case _:
                if arg == '--report-file':
                    print(f"corrupt_file_finder: report-file arguments must appear after file type arguments.")
                    print(f"{help_txt}")
                    exit(1)
                else:
                    print(f"corrupt_file_finder: Invalid argument {args[idx]}")
                    print(f"{help_txt}")
                    exit(1)

    # Remove duplicate file types.
    file_types = list(set(file_types))
    # print(f"file_types: {file_types}")

    # Check target directory to see if it exists and is readable.
    if not os.path.exists(target_dir):
        print(f"corrupt_file_finder: target directory, {target_dir}, does not exist.")
        exit(2)
    if not os.path.isdir(target_dir):
        print(f"corrupt_file_finder: target directory, {target_dir}, is not a directory.")
        exit(2)

    file_list = get_files_from_target_dir(target_dir, file_types, recurse)
    # print(f"file_list: {file_list}")

    # Testing the files. A list of tuples is created for the output.
    test_results = []
    for file in file_list:
        # PurePath often adds a leading period. So, we need to eliminate that from
        # the suffix before using it.
        fp = pathlib.PurePath(file)
        suffix = pathlib.PurePath(file).suffix.replace(".", "")
        # print(f"fp: {fp}. suffix: {suffix}.")
        match suffix:
            case 'pdf':
                result = check_pdf(file)
            case 'zip':
                result = check_zip(file)
        test_results.append((file, result[0], result[1]))

    # Printing results to stdout.
    list_file_types = [f" {file_type}" for file_type in file_types]
    if write_report:
        print(f"corrupt_file_finder: Writing report to {report_file}")
        report = write_report_to_disk(report_file, test_results)
        if not report:
            print(f"corrupt_file_finder: Could not write report to {report_file}")
            exit(4)
    else:
        print(f"corrupt_file_finder: Here are the findings for supported file types,{list_file_types}:")
        for file, result, error_msg in test_results:
            if result:
                print(f"{file}\tusable\tNo errors found")
            else:
                print(f"{file}\tcorrupted\t{error_msg}")
        print("corrupt_file_finder: Report completed.")
