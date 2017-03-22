# -*- coding: utf-8 -*-
import boto3, xlrd, pprint, os, re, collections, csv


def handler(event, context):
  pp = pprint.PrettyPrinter(indent=4)
  data = []
  paths = os.listdir('/Users/tmh/Documents/lambda-siat/data')
  for path in paths:
    #if ".xlsx" in path and "inbound" in path and "2014" in path and "other_groups" in path:
    entry = collections.OrderedDict()
    header_row_index = set_header_row_index(path)
    double_row_header = set_double_row_header(path)
    entry['type'] = set_survey_type(path)
    
    match_group = re.search(r'[0-9]{4}', path)
    if not match_group:
      continue
    entry['year'] = match_group.group()
    book = xlrd.open_workbook('data/' + path)

    for i, sheet in enumerate(book.sheets()):
      data = data + process_rows(sheet, entry, header_row_index, double_row_header)
     
  #pp.pprint(json.dumps(data))    
  write_csv_file(data)
  #return True

def process_rows(sheet, entry, header_row_index, double_row_header):
  question_row_index = 0
  return_data = []

  for row_index in range(sheet.nrows):
    row = sheet.row(row_index)
    if 'TABLE' in row[0].value:
      question_row_index = row_index
    elif row[0].value == '':  # reset question row when blank cell reached
      question_row_index = 0
      continue
    elif is_skippable_row(row[0].value):
      continue
    elif question_row_index != 0:  # if question row is set and other checks pass, process row:
      question = sheet.row(question_row_index)[0].value.strip().replace('*', '')
      answer = row[0].value.strip().replace('*', '')
      for i, cell in enumerate(row):
        if i == 0:
          continue
        entry_copy = entry.copy()
        entry_copy.update({
          'question': question,
          'group': extract_group(sheet, header_row_index, double_row_header, i),
          'number_of_respondents': sheet.row(question_row_index + 1)[i].value,
          'answer': answer,
          'percentage_of_respondents': cell.value
        })
        return_data.append(entry_copy)
  return return_data

def extract_group(sheet, header_row_index, double_row_header, column_index):
  if double_row_header:
    group = sheet.row(header_row_index - 1)[column_index].value.strip() + " " + sheet.row(header_row_index)[column_index].value.strip()
  else:
    group = sheet.row(header_row_index)[column_index].value.strip()
  group = group.replace('\n', '')
  group = re.sub(r'-( )*', '', group)
  return group

def is_skippable_row(first_cell_value):
  return 'Number of Respondents' in first_cell_value or 'Mean' in first_cell_value or 'Median' in first_cell_value

def set_survey_type(path):
  if 'inbound' in path:
    return 'inbound'
  elif 'outbound' in path:
    return 'outbound'

def set_header_row_index(path):
  if '2012' in path or '2013' in path:
    header_row_index = 5
    if 'other_groups' in path:
      header_row_index += 1
  else:
    header_row_index = 4
  return header_row_index

def set_double_row_header(path):
  if '2012' in path or '2013' in path:
    return True
  else:
    return False

def write_csv_file(data):
  keys = data[0].keys()
  with open('entries.csv', 'wb') as csv_file:
    dict_writer = csv.DictWriter(csv_file, keys, quotechar='"')
    dict_writer.writeheader()
    dict_writer.writerows(data)

