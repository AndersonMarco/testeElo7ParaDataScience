import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import mysql.connector

def plot(dates,y):
    years = mdates.YearLocator()   # every year
    months = mdates.MonthLocator()  # every month
    yearsFmt = mdates.DateFormatter('%m/%Y')


    x = [dt.datetime.strptime(d,'%m/%Y').date() for d in dates]


    fig, ax = plt.subplots()
    ax.plot(x,y)
    plt.gcf().autofmt_xdate()
    # format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(yearsFmt)
    ax.xaxis.set_minor_locator(months)

    datemin = np.datetime64(x[0], 'Y')
    datemax = np.datetime64(x[-1], 'Y') + np.timedelta64(1, 'Y')
    ax.format_xdata = mdates.DateFormatter('%Y-%m')
    fig.autofmt_xdate()

    plt.show()
if __name__ == "__main__":    
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="123456",
        database="elo7_datascience",
        get_warnings=False,
        raise_on_warnings=False
    )

    sql="""SELECT sum(rating) as qtyRating, STR_TO_DATE(concat('01/',DATE_FORMAT(timestamp,'%m/%Y')),'%d/%m/%Y') as date FROM elo7_datascience.ratings
           where rating>=3.0
           group by date
           order by date
           """

    cursor = mydb.cursor()
    cursor.execute(sql)
    y=[]
    dates=[]
    for qtyRating, date in cursor:
        y.append(qtyRating)
        dateSplitAtYearMonthDay=str(date).split("-")
        dateMonthYear=dateSplitAtYearMonthDay[1]+"/"+dateSplitAtYearMonthDay[0]
        dates.append(dateMonthYear)

    plot(dates,y)
