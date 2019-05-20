import os
import sys
import csv
from names_dataset import NameDataset
import re
import argparse


def generate_potential_employees(f_path):
    """
    open the email_employee.csv and parse it to create more employees
    """
    f_name = os.path.join(f_path, 'email_employee.csv')
    nd = NameDataset()
    p = re.compile('([a-z]*)\.([a-z]\.)?([a-z]*)@enron.com')
    out_f_name = os.path.join(f_path, 'potential_email_employees.csv')

    num_rows_written = 0

    with open(out_f_name, 'w', newline='') as out_f:
      field_names = ['address', 'firstName', 'lastName']
      writer = csv.DictWriter(out_f, fieldnames = field_names)
      writer.writeheader()

      with open(f_name, 'r') as f:
        reader = csv.DictReader(f, quotechar='"')
        for row in reader:
            eid = row['eid']
            email_id = row['address']
            try:
                v = int(eid)
            except:
                v  = 0

            if v != 0:
                print("found eid: {} for email_id: {}, continuing".format(v, email_id))
                continue
            
            ## match this email id
            m = p.match(email_id)
            if m is None:
                continue

            ## get the groups from this regex
            g = m.groups()

            ## get the first and last names
            fn = g[0]
            ln = g[-1]

            d = {'address': email_id}

            ##  search for the first name in the db
            fn_in_nd = nd.search_first_name(fn)
            if not fn_in_nd and nd.search_first_name(ln):
                ## swap the two
                d['firstName'] = ln
                d['lastName'] = fn
            else:
                ## continue as default
                d['firstName'] = fn
                d['lastName'] = ln

            ## write this to the output file as a row
            writer.writerow(d)
            num_rows_written += 1
    
    print("wrote {} rows of data to the file: {}".format(num_rows_written, out_f_name))

if __name__ == '__main__':
    desc = """Generate potential employees based on email signatures.

A lot of email addresses in the db don't have corresponding Employee ids. 
However, their email addresses (@enron.com)  suggest that they might be 
employees. In addition, their email addresses follow the pattern 
<firstName>.<lastName>@enron.com.

For these email addresses, nodes labelled PotentialEmployee are generated
in the table so that the search experience is richer. The names_dataset
module is used to check the order of first names and last names in their 
email addresses. When it seems more likely that their address was 
<secondName>.<firstName>, these names are swapped around.
"""
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--path', dest='path', type=str, help='path to email_employees.csv file', default='.')
    args = parser.parse_args()
    generate_potential_employees(args.path)
