from django.core.exceptions import ObjectDoesNotExist

from product_guide.models import File


class UploadFiles:

    def __init__(self, file_name):
        self.file_name = UploadFiles.set_correct_file_name(file_name)
        self.file_type = UploadFiles.determine_file_type(self.file_name)

    @staticmethod
    def set_correct_file_name(file_name):

        if ' ' in file_name:
            file_name = file_name.replace(' ', '_')
        if '№' in file_name:
            file_name = file_name.replace('№', '')
        if '(' in file_name:
            file_name = file_name.replace('(', '')
        if ')' in file_name:
            file_name = file_name.replace(')', '')

        return file_name

    @staticmethod
    def determine_file_type(file_name):
        """Определение типа файла.
            Функция принимает имя файла, возвращает строку 'msexcel' или 'msword'."""

        if file_name.endswith('.xls') or file_name.endswith('.xlsx'):
            return 'msexcel'
        elif file_name.endswith('.doc') or file_name.endswith('.docx'):
            return 'msword'




class FileProcessing:
    pass