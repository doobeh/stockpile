from stockpile import app, db
from stockpile.models import Physical, StockPile
from trickle import reader_old, reader_new
from datetime import datetime, timedelta, date, time


with app.app_context():

    ## IGA Queries:

    comparison_query = Physical.query.filter(
        Physical.created > datetime(2014, 9, 16, 0, 0, 0)
    ).filter(
        Physical.created < datetime(2014, 10, 5, 23, 59, 59)
    ).order_by(
        Physical.created.asc()
    ).all()

    iga_pre_count = Physical.query.filter(
        Physical.created > datetime(2014, 9, 16, 0, 0, 0)
    ).filter(
        Physical.created < datetime(2014, 9, 30, 0, 0, 0)
    ).filter(
        Physical.store == 1
    ).order_by(
        Physical.created.asc()
    ).all()

    iga_pre_count_two = Physical.query.filter(
        Physical.created > datetime(2014, 9, 30, 0, 0, 0)
    ).filter(
        Physical.created < datetime(2014, 9, 30, 23, 59, 59)
    ).filter(
        Physical.user.ilike('%leroy%')
    ).filter(
        Physical.store == 1
    ).order_by(
        Physical.created.asc()
    ).all()

    iga_floor = Physical.query.filter(
        Physical.created > datetime(2014, 9, 30, 0, 0, 0)
    ).filter(
        Physical.created < datetime(2014, 9, 30, 23, 59, 59)
    ).filter(
        ~Physical.user.ilike('%leroy%')
    ).filter(
        Physical.store == 1
    ).order_by(
        Physical.created.asc()
    ).all()

    iga_post_count = Physical.query.filter(
        Physical.created > datetime(2014, 9, 30, 23, 59, 59)
    ).filter(
        Physical.created < datetime(2014, 10, 5, 23, 59, 59)
    ).filter(
        Physical.store == 1
    ).order_by(
        Physical.created.asc()
    ).all()

    ## GG Queries

    gg_pre_count = Physical.query.filter(
        Physical.created > datetime(2014, 9, 16, 0, 0, 0)
    ).filter(
        Physical.created < datetime(2014, 9, 30, 23, 59, 59)
    ).filter(
        Physical.store == 3
    ).order_by(
        Physical.created.asc()
    ).all()

    gg_store = Physical.query.filter(
        Physical.created > datetime(2014, 10, 1, 0, 0, 0)
    ).filter(
        Physical.created < datetime(2014, 10, 1, 23, 59, 59)
    ).filter(
        Physical.store == 3
    ).order_by(
        Physical.created.asc()
    ).all()

    gg_post_count = Physical.query.filter(
        Physical.created > datetime(2014, 10, 1, 23, 59, 59)
    ).filter(
        Physical.created < datetime(2014, 10, 5, 23, 59, 59)
    ).filter(
        Physical.store == 3
    ).order_by(
        Physical.created.asc()
    ).all()


    # print len([x for x in comparison_query])
    # print len([x for x in iga_pre_count])
    # print len([x for x in iga_pre_count_two])
    # print len([x for x in iga_floor])
    # print len([x for x in iga_post_count])
    # print len([x for x in gg_pre_count])
    # print len([x for x in gg_store])
    # print len([x for x in gg_post_count])

    store_locations = {
        '001': r'\\10.0.0.229\c$\pcmaster\trickle\arc',
        '003': r'\\10.0.2.220\c$\pcmaster\trickle',
    }

    def sales(product, time, results, shop_time=15):
        origin = (datetime.combine(datetime.today(), time) + timedelta(minutes=shop_time)).time()
        for sale in results:
            if sale["product"] == product:
                if sale["time"] > origin:
                    print sale

    ## IGA FLOOR SALES ##########################

    first_occurrence = dict()

    for item in iga_floor:
        if item.item_id:
            if not first_occurrence.get(item.item_id):
                first_occurrence['{:013d}'.format(item.item_id)] = item.created.time()

    iga_floor_dt = date(2014, 9, 30)
    results = reader_new(location=store_locations.get('001'), dt=iga_floor_dt)

    for sale in results:
        if first_occurrence.get(sale["product"]):
            # Sold and scanned.
            shopping_window = 15
            boundary = (datetime.combine(
                datetime.today(), first_occurrence.get(sale["product"])
            ) + timedelta(minutes=shopping_window)).time()

            if sale["time"] > boundary:
                # Add Sale to StockPile
                db.session.add(StockPile.from_sale(sale, 1))
                print '{store} SALE {time}: {product}={quantity}@{sale}'.format(
                    store='001',
                    time=boundary.strftime("%H%M"),
                    product=sale["product"],
                    quantity=sale["qty"] * -1,
                    sale=sale["time"]
                )

    ## GG FLOOR SALES  ##########################

    first_occurrence = dict()

    for item in gg_store:
        if item.item_id:
            if not first_occurrence.get(item.item_id):
                first_occurrence['{:013d}'.format(item.item_id)] = item.created.time()

    gg_floor_dt = date(2014, 10, 1)
    results = reader_old(location=store_locations.get('003'), dt=gg_floor_dt)

    for sale in results:
        if first_occurrence.get(sale["product"]):
            # Sold and scanned.
            shopping_window = 15
            boundary = (datetime.combine(
                datetime.today(), first_occurrence.get(sale["product"])
            ) + timedelta(minutes=shopping_window)).time()

            if sale["time"] > boundary:
                # Add Sale to StockPile
                db.session.add(StockPile.from_sale(sale, 3))
                print '{store} SALE {time}: {product}={quantity}@{sale}'.format(
                    store='003',
                    time=boundary.strftime("%H%M"),
                    product=sale["product"],
                    quantity=sale["qty"],
                    sale=sale["time"]
                )

    db.session.commit()

    # for x in gg_store:
    #     if x.item:
    #         print '{product:013d} {description:<30} {store} {created} {user}'.format(
    #             product=x.item_id,
    #             description=x.item.description.encode('latin-1'),
    #             store=x.store,
    #             user=x.user.upper(),
    #             created=x.created
    #         )

    for iterable in [iga_pre_count, iga_pre_count_two, iga_floor,
                     iga_post_count, gg_pre_count, gg_store, gg_post_count]:
        for x in iterable:
            db.session.add(StockPile.from_physical(x))
        db.session.commit()



    # Load the physical count into the stockpile.
    # Isolate a result-set that shows just the shop-floor count (IGA)
    # Load the sales we care about from the 30th IGA into the stockpile.
    # Isolate a result-set that shows just the perishable shop-floor count (IGA)
    # Load the sales we care about from the 1st GG into the stockpile.
    # Load the sales