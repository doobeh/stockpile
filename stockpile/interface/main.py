from flask import Blueprint, render_template, flash, request, redirect, url_for
from datetime import datetime, timedelta, date
from sqlalchemy import func, not_
from trickle import reader
from collections import defaultdict

from stockpile.models import Item, Physical

mod = Blueprint('interface', __name__, template_folder='templates')

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



@mod.route('/iga-missed-items/')
def missed_items():

    iga_floor = Physical.query.filter(
        Physical.created > datetime(2014, 9, 30, 0, 0, 0)
    ).filter(
        Physical.created < datetime(2014, 9, 30, 23, 59, 59)
    ).filter(
            not_(
                Physical.user.ilike('leroy')
            )
    ).filter(
            Physical.store==1
    ).order_by(
        Physical.created.asc()
    ).all()

    first_occurence = dict()

    for item in iga_floor:
        if item.item_id:
            if not first_occurence.get(item.item_id):
                first_occurence['{:013d}'.format(item.item_id)] = item.created.time()

    dt = date(2014, 9, 30)
    results = reader(location=store_locations.get('001'), dt=dt)

    missed_items = list()
    for sale in results:
        if first_occurence.get(sale["product"]):
            # Sold and scanned.
            shopping_window = 15
            boundary = (datetime.combine(
                datetime.today(), first_occurence.get(sale["product"])
            ) + timedelta(minutes=shopping_window)).time()

            if sale["time"] > boundary:
                # create entry for stockpile.
                pass
        else:
            # Sold by not scanned?!
            if sale["product"].startswith(('0024','000000000')):
                pass
            else:
                missed_items.append(sale["product"])

    not_scanned = list()
    for entry in set(missed_items):
        item = Item.query.filter_by(upc=int(entry)).first()
        if item and item.department_id and item.department_id not in (30, 40, 41, 20, 22):
            not_scanned.append(item)

    return render_template('interface/missed_items.html', missed=not_scanned)




@mod.route('/tick/')
def shop_floor_iga():
    start_date = datetime(2014, 9, 30, 0, 0, 0)
    end_date = datetime(2014, 9, 30, 23, 59, 59)

    iga_floor = Physical.query.filter(
        Physical.created>start_date
    ).filter(
        Physical.created<end_date
    ).filter(
            not_(
                Physical.user.ilike('leroy')
            )
    ).filter(
            Physical.store==1
    ).order_by(
        Physical.created.asc()
    ).all()

    return render_template('interface/iga_floor.html', results=iga_floor)