"""
CIS 3680 Team Project
Team print("Hello World!")
Chris, Adrian, Luis, John
"""

import csv

END_OF_HEADER = "*" * 25

def write_record(writer, rpt_data, defend_data, offense_data):
    rec = {}
    rec.update(rpt_data)
    rec.update(defend_data)
    rec.update(offense_data)
    writer.writerow(rec)

def is_summary_header(line):
    return line[0] == '1' and "RUN DATE:" in line

def is_page_header(line):
    return line[0] == '1' and "RUN DATE:" not in line

def process_page_header(infile):
    while True:
        line = infile.readline()

        if END_OF_HEADER in line:
            break

def is_report_header(line):
    return line[0] != '1' and "RUN DATE:" in line

def process_report_header(infile, line):
    rec = {}

    rec['RunDate'] = line[12:22].strip()

    while True:
        line = infile.readline()

        if END_OF_HEADER in line:
            break
        elif "COURT DATE:" in line:
            rec['CourtDate'] = line[22:32].strip()
            rec['CourtTime'] = line[44:52].strip()
            rec['CourtRoom'] = line[78:].strip()

    return rec

def is_defend(line):
    try:
        int(line[0:6])
        return True
    except ValueError:
        return False

def process_defend(line):
    defend = {}

    defend['number'] = line[0:6].strip()
    defend['fileNumber'] = line[8:20].strip()
    defend['name'] = line[20:42].strip()
    defend['complainant'] = line[42:57].strip()

    # add default values for optional fields
    
    defend['language'] = 'English'
    defend['fingerprint'] = 'No' # defendant does not need fingerprinted
    defend['AKA'] = 'n/a'
    defend['bond'] = 'n/a'

    if len(line) >= 85:
        defend['attorney'] = line[66:84].strip()
        defend['CONT'] = line[84:].strip()
    elif len(line) >= 67:
        defend['attorney'] = line[66:].strip()
        defend['CONT'] = ''
    else:
        defend['attorney'] = ''
        defend['CONT'] = ''

    return defend

def process_off_L1(line):
    offense = {}

    offense['charge'] = line[8:44].strip()
    offense['plea'] = line[49:65].strip()
    offense['verdict'] = line[76:83].strip()

    return offense

def process_off_L2(line, offense_data):
    offense_data['CLS'] = line[12:15].strip()
    offense_data['P'] = line[17:20].strip()
    offense_data['L'] = line[22:28].strip()
    offense_data['DOM VL'] = line[35:40].strip()
    offense_data['judgement'] = line[49:76].strip()
    offense_data['ADA'] = line[81:].strip()

FIELDNAMES = ['RunDate','CourtDate', 'CourtTime', 'CourtRoom', 'number', 'fileNumber', 'name', 'complainant', 'language', 'fingerprint', 'AKA', 'bond', 'attorney', 'CONT', 'charge', 'plea', 'verdict', 'CLS', 'P', 'L', 'DOM VL', 'judgement', 'ADA']

def main():
    # filename = input("Enter the court data you'd like to process: ")
    filename = r"CalendarData2021\DISTRICT.DISTRICT_COURT_.11.03.21.AM.9999.CAL.txt"

    infile = open(filename, 'r')

    csvfile = open("results.csv", 'w', newline = '')
    writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
    writer.writeheader()
    
    rpt_data = {}
    defend_data = {}
    offense_data = {}

    while True:
        line = infile.readline()

        if line == "" or is_summary_header(line):
            break
        elif line == "\n":
            pass
        elif is_page_header(line):
            process_page_header(infile)
        elif is_report_header(line):
            rpt_data = process_report_header(infile, line)
        elif is_defend(line):
            if len(defend_data) > 0:
                write_record(writer, rpt_data, defend_data, offense_data)
                defend_data = {}
                offense_data = {}
            defend_data = process_defend(line)
        elif "FINGERPRINTED" in line:
            defend_data['fingerprint'] = 'Yes' # defendant needs fingerprinted
        elif "AKA:" in line:
            defend_data['AKA'] = line[19:].strip()
        elif "SPANISH" in line:
            defend_data['language'] = line[19:].strip()
        elif "BOND:" in line:
            defend_data['bond'] = line[25:41].replace(',', '').strip() 
        elif "PLEA:" in line:
            if len(offense_data) > 0:
                write_record(writer, rpt_data, defend_data, offense_data)
                offense_data = {}
            offense_data = process_off_L1(line)
        elif "JUDGMENT:" in line:
            process_off_L2(line, offense_data)
        else:
            print(line, end="")
    
    write_record(writer, rpt_data, defend_data, offense_data)

    csvfile.close()
    infile.close()
    

if __name__ == '__main__':
    main()
