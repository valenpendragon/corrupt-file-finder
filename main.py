import zipfile
import pypdf
import sys
import os
import glob


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
            print(f"Opening PDF, {filepath}, produced Exception: {e}")
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
                print(f"The first bad file in {filepath} is {ret}")
                result = (False, {ret})
            else:
                result = (True, None)
            return result
        except Exception as e:
            print(f"Opening zip file, {filepath}, produced Exception: {e}")
            result = (False, e)
            return result


if __name__ == "__main__":
    args = sys.argv
    len_args = len(args)
    valid_arguments = ['-p', '--pdf', '-z', '--zip']
    print(f"args: {args}")

    help_txt = "Usage: main.py [-p|--pdf] [-z|--zip] directory"

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

    # Identify target directory and remove it from arguments.
    target_dir = args[-1]
    args.pop(-1)
    print(f"target_dir: {target_dir}")

    # Setting up file types to examine.
    file_types = []

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
            case _:
                print(f"corrupt_file_finder: Invalid argument {args[idx]}")
                print(f"{help_txt}")
                exit(1)

    # Remove duplicate file types.
    file_types = list(set(file_types))
    print(f"file_types: {file_types}")
