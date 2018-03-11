import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd

import plotly
plotly.tools.set_credentials_file(username='haedong', api_key='L5VyzlZ6wFZjqaSCdqwQ')
import pymysql

host = "211.253.10.91"
user = "root"
pwd = "goehddl"
dbname = "haedong4"
DB_CHARSET = "utf8"

conn = pymysql.connect(host='211.253.10.91', user='root', password='goehddl', db='haedong4', charset='utf8')
cur = conn.cursor()


def request_tick_candle(subject_code, tick_unit, start_date='20171205', end_date='20171205'):
    query = '''
    select t1.id
         , t1.date
         , t1.high
         , t1.low
         , t2.price as open
         , t3.price as close
      from (
            select Floor((result.row-1) / '%s') + 1 as id
                 , min(date_format(result.date, '%%Y%%m%%d%%H%%i%%s')) as date
                 , max(result.id) as max_id
                 , min(result.id) as min_id
                 , max(result.price) as high
                 , min(result.price) as low
              from (
                    select @rownum:=@rownum+1 as row
                         , id
                         , price
                         , date
                      from %s s1
                     inner join (
                                select @rownum:=0
                                  from dual
                                ) s2

                    where s1.date between Date('%s-%s-%s') and Date('%s-%s-%s')
                   ) result
             group by Floor((result.row-1) / '%s')
           ) t1
     inner join %s t2
        on t1.min_id = t2.id
     inner join %s t3
        on t1.max_id = t3.id
    ;
    ''' % (
    tick_unit, subject_code, start_date[:4], start_date[4:6], start_date[6:], end_date[:4], end_date[4:6], end_date[6:],
    tick_unit, subject_code, subject_code)

    return query


#df = pd.read_csv('oil.csv')
df = pd.read_sql(request_tick_candle("GCG18", 60, start_date='20171205', end_date='20171205'), conn)

print(df)

trace = go.Candlestick(x=df.id,
                       open=df.open,
                       high=df.high,
                       low=df.low,
                       close=df.close)
data = [trace]
layout = {
    'title': 'The Great Recession',
    'yaxis': {'title': 'AAPL Stock'},
    'shapes': [{
        'x0': '2016-12-09', 'x1': '2016-12-09',
        'y0': 0, 'y1': 1, 'xref': 'x', 'yref': 'paper',
        'line': {'color': 'rgb(30,30,30)', 'width': 1}
    }],
    'annotations': [{
        'x': '2016-12-09', 'y': 0.05, 'xref': 'x', 'yref': 'paper',
        'showarrow': False, 'xanchor': 'left',
        'text': 'Increase Period Begins'
    }]
}

fig = dict(data=data, layout=layout)
py.plot(fig, filename='aapl-recession-candlestick')