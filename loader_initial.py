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


    print len([x for x in comparison_query])
    print len([x for x in iga_pre_count])
    print len([x for x in iga_pre_count_two])
    print len([x for x in iga_floor])
    print len([x for x in iga_post_count])
    print len([x for x in gg_pre_count])
    print len([x for x in gg_store])
    print len([x for x in gg_post_count])

    store_locations = {
        '001': r'\\10.0.0.229\c$\pcmaster\trickle\arc',
        '003': r'\\10.0.2.220\c$\pcmaster\trickle\archive',
    }

    def sales(product, time, results, shop_time=15):
        origin = (datetime.combine(datetime.today(), time) + timedelta(minutes=shop_time)).time()
        for sale in results:
            if sale["product"] == product:
                if sale["time"] > origin:
                    print sale

    first_occurence = dict()

    for item in iga_floor:
        if item.item_id:
            if not first_occurence.get(item.item_id):
                first_occurence['{:013d}'.format(item.item_id)] = item.created.time()

    iga_floor_dt = date(2014, 9, 30)
    results = reader_new(location=store_locations.get('001'), dt=iga_floor_dt)

    missed_items = list()

    for sale in results:
        if first_occurence.get(sale["product"]):
            # Sold and scanned.
            shopping_window = 15
            boundary = (datetime.combine(
                datetime.today(), first_occurence.get(sale["product"])
            ) + timedelta(minutes=shopping_window)).time()

            if sale["time"] > boundary:
                print 'SALE {time}: {product}={quantity}@{sale}'.format(
                    time=boundary.strftime("%H%M"),
                    product=sale["product"],
                    quantity=sale["qty"],
                    sale=sale["time"]
                )
            else:
                print 'EARL {time}: {product}={quantity}@{sale}'.format(
                    time=boundary.strftime("%H%M"),
                    product=sale["product"],
                    quantity=sale["qty"],
                    sale=sale["time"]
                )
        else:
            # Sold by not scanned?!
            boundary = time(0, 0)
            if sale["product"].startswith(('0024', '000000000')):
                pass
            else:
                print 'SNS  {time}: {product}={quantity}@{sale}'.format(
                    time=boundary.strftime("%H%M"),
                    product=sale["product"],
                    quantity=sale["qty"],
                    sale=sale["time"]
                )

    # for x in gg_store:
    #     if x.item:
    #         print '{product:013d} {description:<30} {store} {created} {user}'.format(
    #             product=x.item_id,
    #             description=x.item.description.encode('latin-1'),
    #             store=x.store,
    #             user=x.user.upper(),
    #             created=x.created
    #         )

    # Load the physical count into the stockpile.
    # Isolate a result-set that shows just the shop-floor count (IGA)
    # Load the sales we care about from the 30th IGA into the stockpile.
    # Isolate a result-set that shows just the perishable shop-floor count (IGA)
    # Load the sales we care about from the 1st GG into the stockpile.
    # Load the sales