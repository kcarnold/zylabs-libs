#!/usr/bin/env python

import pandas as pd
import json

# Load report
report = pd.read_csv("report.csv")
report['calvin_id'] = report['School email'].str.split('@', expand=True).iloc[:,0]
indexed_report = report.set_index('calvin_id').copy()

# Load partners data
partners = json.load(open('partners.json'))


# Get column names
lab_names = sorted(partners.keys())
lab_column_names = [col for col in indexed_report.columns if '- Lab' in col]
lab_name_to_column = {
    lab_name: col_name
    for lab_name, col_name in zip(
        lab_names,
        lab_column_names
    )
}
print(lab_name_to_column)


# Give every student in the group the max score of any submission in the group, part by part
for lab_name, partners_for_this_part in partners.items():
    lab_column = lab_name_to_column[lab_name]
    for group in partners_for_this_part:
        scores = [indexed_report.loc[student_id, lab_column] for student_id in group]
        # TODO(kca): figure out why max() did the right thing with `nan`s (and what are these nan objects anyway?)
        max_score = max(scores)
        #print(lab_name, max_score, len(group))
        
        for student_id in group:
            indexed_report.loc[student_id, lab_column] = max_score


# Compute weighted sum of scores

# extract point values
import re
weights = [int(re.search(r'\((\d+)\)$', col_name).group(1)) for col_name in lab_column_names]

# normalize
total_weight = sum(weights)
weights = [w / total_weight for w in weights]


# fill in missing scores with zeros
indexed_report.fillna(0, inplace=True)

# Compute total scores
indexed_report['lab_scores'] = (
    sum([w * indexed_report.loc[:, col_name] for w, col_name in zip(weights, lab_column_names)])
).round(2)

# Write output
indexed_report.to_csv(f'merged_scores.csv')

