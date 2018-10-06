from mooc.models import Number
import xlrd

Num = Number.objects.all()
file = '360741-363120.xls'
xls = xlrd.open_workbook(filename=file)
sheet = xls.sheet_by_name('360741-363120')
for i in range(sheet.nrows):
    ming_ma = sheet.cell(i,0).value
    an_ma = sheet.cell(i,1).value
    num = Number(ming_ma=ming_ma, an_ma=an_ma)
    try:
        num.save()
    except:
        print("该信息有误:明码：{}，暗码：{}".format(ming_ma,an_ma))

