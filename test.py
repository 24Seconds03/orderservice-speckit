import sqlite3
con=sqlite3.connect('orders.db')
cur=con.cursor()
print('tables=', cur.execute("select name from sqlite_master where type='table'").fetchall())
print('outbox=', cur.execute('select event_type, aggregate_id, occurred_at from  outbox_events order by created_at desc limit 10').fetchall())