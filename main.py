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
