"""HEX OS X V34 subsystem adapter: calendar."""
def run(ctx):
 import calendar,datetime
 year=int(ctx['data'].get('year',datetime.date.today().year));month=int(ctx['data'].get('month',datetime.date.today().month));assert 1900<=year<=2200 and 1<=month<=12
 return {'year':year,'month':month,'weeks':calendar.monthcalendar(year,month)}
