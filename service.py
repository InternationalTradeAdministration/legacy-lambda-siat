# -*- coding: utf-8 -*-
import boto3, xlrd, pprint, os, re, collections, csv, uuid, json

group_mappings = {
  "No":                 "Package:  No",               
  "Repeat":             "Frequency of visit:  Repeat",
  "Vacation":           "Purpose of trip:  Vacation",
  "Yes":                "Package:  Yes",
  "First":              "Frequency of visit:  First",
  "Airline":            "Transportation:  Airline",
  "Train":              "Transportation:  Train",
  "Rental Car":         "Transportation:  Rental Car",
  "Vacation and VFR":   "Purpose of trip:  Vacation and VFR",
  "Hotel/ Motel":       "Hotel/Motel",
  "Bus. and Conv.":     "Purpose of trip:  Business and Convention",
  "Convention":         "Purpose of trip:  Convention",
  "Business":           "Purpose of trip:  Business",
  "Airlines in U.S.":   "Transportation:  Airlines in U.S."
}

s3 = boto3.resource('s3')

def handler(event, context):
  bucket_name = event['Records'][0]['s3']['bucket']['name']
  bucket = s3.Bucket(bucket_name)
  pp = pprint.PrettyPrinter(indent=4)
  data = []

  for obj in bucket.objects.all():
    path = obj.key
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), path)
    bucket.download_file(path, download_path)

    entry = collections.OrderedDict()
    header_row_index = set_header_row_index(path)
    double_row_header = set_double_row_header(path)
    entry['type'] = set_survey_type(path)
    
    match_group = re.search(r'[0-9]{4}', path)
    if not match_group:
      continue
    entry['year'] = match_group.group()
    book = xlrd.open_workbook(download_path)

    for i, sheet in enumerate(book.sheets()):
      data = data + process_rows(sheet, entry, header_row_index, double_row_header)
     
  #pp.pprint(json.dumps(data))    
  write_csv_file(data)

def process_rows(sheet, entry, header_row_index, double_row_header):
  question_row_index = 0
  return_data = []

  for row_index in range(sheet.nrows):
    row = sheet.row(row_index)
    if is_question_row(row[0].value):
      question_row_index = row_index
    elif row[0].value == '':  # reset question row if blank cell reached
      question_row_index = 0
      continue
    elif is_skippable_row(row[0].value):
      continue
    elif question_row_index != 0:  # if question row is set and other checks pass, process row:
      return_data = return_data + entries_from_row(sheet, row, entry, question_row_index, header_row_index, double_row_header)
  return return_data

def entries_from_row(sheet, row, entry, question_row_index, header_row_index, double_row_header):
  return_data = []
  question = extract_question(sheet, question_row_index)
  answer = row[0].value.strip().replace('*', '')
  for i, cell in enumerate(row):
    if i == 0:
      continue
    entry_copy = entry.copy()
    entry_copy.update({
      'question': question,
      'group': extract_group(sheet, header_row_index, double_row_header, i),
      'number_of_respondents': extract_number_of_respondents(sheet, question_row_index, i),
      'answer': answer,
      'percentage_or_value': extract_cell_value(cell)
    })
    return_data.append(entry_copy)
  return return_data

def extract_group(sheet, header_row_index, double_row_header, column_index):
  if double_row_header:
    group = sheet.row(header_row_index - 1)[column_index].value.strip() + " " + sheet.row(header_row_index)[column_index].value.strip()
    group = group.strip()
  else:
    group = sheet.row(header_row_index)[column_index].value.strip()
  group = group.replace('\n', '').replace('  ', ' ').replace('&', 'and')
  group = re.sub(r'-( )*', '', group)
  if group in group_mappings:
    group = group_mappings[group]
  return group

def extract_cell_value(cell):
  value = cell.value
  if value == '-':
      value = 0
  return value

def extract_question(sheet, question_row_index):
  question = sheet.row(question_row_index)[0].value.strip().replace('*', '')
  return re.sub(r'((T)*ABLE [0-9]+ - )?Q[0-9]+[a-z]*.(/)?(Q)?[0-9]*[a-z]*(.)?', '', question)

def extract_number_of_respondents(sheet, question_row_index, column_index):
  value = sheet.row(question_row_index + 1)[column_index].value
  if value < 0:
    value = value * -1
  return value

def is_skippable_row(first_cell_value):
  return 'Number of Respondents' in first_cell_value or 'Mean' in first_cell_value or 'Median' in first_cell_value

def is_question_row(row_val):
  return re.search(r'Q[0-9]+[a-z]+', row_val)

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
  with open('/tmp/entries.csv', 'wb') as csv_file:
    dict_writer = csv.DictWriter(csv_file, keys, quotechar='"')
    dict_writer.writeheader()
    dict_writer.writerows(data)
  response = s3.Object('siat-csv', 'entries.csv').put(Body=open('/tmp/entries.csv').read(), ContentType='application/csv', ACL='public-read')


