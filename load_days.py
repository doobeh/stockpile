from stockpile import app, db
from stockpile.models import Physical, StockPile, Item
from datetime import datetime, timedelta, date, time
import re

with app.app_context():
    iga_plu_sales_file = r'e:\ISS45\001_plu_sales.txt'
    gg_plu_sales_file = r'e:\ISS45\003_plu_sales.txt'

    iga_products = file(iga_plu_sales_file, 'r')
    fourth = datetime(2014, 10, 4)

    def process_date(dt, store, sales_file):
        iss_file = file(sales_file, 'r')

        data_filter = r'^ (?P<date>{yr}-{month:02d}-{day}) 00:00:00.000'.format(
            yr=dt.year,
            month=dt.month,
            day=dt.strftime("%d"),
        )

        products = [x.upc for x in Item.query.all()]

        for line in iss_file:
            m = re.match(data_filter, line)

            if not m:
                continue

            plu = int(line[25:47].strip())
            dt = datetime.strptime(m.group("date"), '%Y-%m-%d')
            sales = round(float(line[108:129]), 2)
            quantity = round(float(line[130:154]), 2)
            weighted = int(line[100:107].strip())
            if plu in products:
                if weighted:
                    db.session.add(
                        StockPile.from_iss_row(plu, dt, sales, int(quantity), store, weight=quantity)
                    )
                else:
                    db.session.add(
                        StockPile.from_iss_row(plu, dt, sales, quantity, store, weight=0)
                    )
        db.session.commit()

    active_date = datetime(2014, 10, 4)
    process_date(active_date, 3, gg_plu_sales_file)
