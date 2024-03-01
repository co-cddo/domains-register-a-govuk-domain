import os
import csv

from django.conf import settings


def handle_uploaded_file(file):
    file_path = os.path.join(settings.MEDIA_ROOT, file.name)
    with open(file_path, "wb+") as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def organisations_list() -> list:
    """
    Hard coded path for now
    (
        ("Unread", ("Unread")),
        ("Read", ("Read"))
    )
    """
    csv_filename = os.path.join(os.getcwd(),
                                'request_a_govuk_domain',
                                'input/organisations.csv')
    data = [("", "")]
    with open(csv_filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append((row[0], (row[0])))
    return data
