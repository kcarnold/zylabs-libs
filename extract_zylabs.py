#!/usr/bin/env python
#
# 1. Download all submissions from the ZyLab. Don't extract. Rename as `lab3A.zip` or whatever.
# 2. Download an Assignment Report from ZyBooks (it doesn't matter which), save as report.csv. This is used only for school emails.
# 3. Run this script from the directory that includes the zipfile. It extracts the zip files and names them based on all partners.
# 4. See credit_partners.py if you want to automatically update the report spreadsheets to credit partners in pair programming.

import zipfile
import pathlib
import io
import pandas as pd

working_dir = pathlib.Path('.')

try:
    report = pd.read_csv('report.csv')
    all_student_ids = list(report['School email'].str.split('@', expand=True).iloc[:,0])
except:
    all_student_ids = []
    print("Warning: failed to load school emails from report.csv; partner-crediting functionality is disabled.")
    print()

def get_submissions_for_assignment(zip_filename):
    all_students_zipfile = zipfile.ZipFile(zip_filename)

    # The solutions zipfile contains zipfiles for each student submission.
    # The names are based on the student who *submitted*, but they may also have had a *partner*.
    return [get_data_for_submission(all_students_zipfile, student_zipfile_name) for student_zipfile_name in all_students_zipfile.namelist()]


def get_data_for_submission(all_students_zipfile, student_zipfile_name):
    # Names may have multiple parts, so split from the end.
    name, email, date, time = student_zipfile_name[:-4].rsplit('_', 3)

    # Try to normalize the email address into a user id.
    email = email.lower()
    if email.endswith('calvin.edu'):
        email = email[:-len('calvin.edu')]
    student_id = email
    assert len(student_id) < 10

    # Open this student's zipfile.
    this_student_zipfile_data = all_students_zipfile.open(student_zipfile_name).read()
    this_student_zipfile = zipfile.ZipFile(
        io.BytesIO(this_student_zipfile_data)
    )

    submission_files = {}
    for name_in_user_file in this_student_zipfile.namelist():
        contents = this_student_zipfile.open(name_in_user_file).read().decode('utf8')
        submission_files[name_in_user_file] = contents
    other_authors = {author for content in submission_files.values() for author in get_credited_authors(content)}
    if all_student_ids != []:
        if student_id not in other_authors:
            print("Submitting student didn't include their id:", student_id)
        else:
            other_authors.remove(student_id)
            if other_authors:
                print(f"{student_id} also credited {', '.join(other_authors)}")
    return dict(
        name=name.replace('_', ' '),
        student_id=student_id,
        date=date,
        time=time,
        files=submission_files,
        other_authors=other_authors
    )


def get_credited_authors(contents, be_conservative=False):
    lower_contents = contents.lower()
    authors = [student_id for student_id in all_student_ids if student_id in lower_contents]
    if be_conservative:
        if authors and len(authors) == lower_contents.count('author:'):
            return authors
        # Otherwise be conservative; we don't know the authors.
        return None
    return authors


# For each lab solutions zipfile downloaded from ZyLabs...  
all_zipfiles = list(working_dir.glob('*.zip'))
assert len(all_zipfiles) < 10, "Lots of zipfiles, are you sure this is the right directory?"
if len(all_zipfiles) == 0:
    print("No zipfiles found!")

partners = {}
for zip_filename in sorted(all_zipfiles):
    stem = zip_filename.stem
    print("\nExtracting Assignment:", stem)
    submissions = get_submissions_for_assignment(zip_filename)

    # Write 'lab1_0.zip' contents to the 'lab1_0' directory, etc.
    out_dir = working_dir / stem
    out_dir.mkdir(exist_ok=True)

    partners[stem] = partners_for_this_part = []
    all_students_seen = set()
    for submission in submissions:
        all_authors = [submission['student_id']] + sorted(submission['other_authors'])
        partners_for_this_part.append(all_authors)
        all_students_seen.update(all_authors)

        submission_dirname = '_'.join(all_authors)
        submission_dir = out_dir / submission_dirname
        submission_dir.mkdir(exist_ok=True, parents=True)
        for name_in_user_file, contents in submission['files'].items():
            (submission_dir / name_in_user_file).write_text(contents, encoding="utf-8")

    missing_students = [student_id for student_id in all_student_ids if student_id not in all_students_seen]
    if missing_students:
        print(f"{stem}: Didn't see anything from students: ", ', '.join(missing_students))

import json
json.dump(partners, open('partners.json', 'w'))
