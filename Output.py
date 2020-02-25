import xlsxwriter


def write_answers_to_exel(answ, str_types,str_answers):
    workbook = xlsxwriter.Workbook('student1_checked.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0
    # Iterate over the data and write it out row by row.
    for key, val in answ.items():
        worksheet.write(row, col, key)
        worksheet.write(row, col + 1, val)
        worksheet.write(row, col + 2, str_answers[key - 1])
        row += 1
    workbook.close()