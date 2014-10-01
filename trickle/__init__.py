import os
import xml.etree.ElementTree as Et
from datetime import time


def reader(location, dt):
    product_sales = list()
    totals = 0
    files = [os.path.join(location, x) for x in os.listdir(location) if dt.strftime('TRPER%Y%m%d') in x]
    for xml_file in files:
        file_sales, ticket_total = process_file(xml_file)
        product_sales += file_sales
        totals += ticket_total
    print totals / 100.0
    return product_sales


def process_file(xml_file):
    product_sales = list()

    tree = Et.parse(os.path.join(xml_file))
    root = tree.getroot()

    ticket_total = 0
    for child in root:
        child_sales = list()
        for subcode in child:
            if subcode.tag == 'PluSale':
                if int(subcode.attrib.get('QtyIsWeight')):
                    qty = 1
                    weight = int(subcode.attrib.get('Qty'))
                else:
                    qty = int(subcode.attrib.get('Qty'))
                    weight = 0

                child_sales.append({
                    'product': subcode.attrib.get('PluCode')[1:],
                    'price': int(subcode.attrib.get('Price')),
                    'amount': int(subcode.attrib.get('Amount')),
                    'weight': weight,
                    'qty': qty,
                    'time': time(
                        int(subcode.attrib.get('Time')[0:2]),
                        int(subcode.attrib.get('Time')[3:5]),
                        int(subcode.attrib.get('Time')[6:8])
                    ),
                    'ticket': int(subcode.attrib.get('TicketNumber')),
                    'pos': int(subcode.attrib.get('PosNo')),
                })
            # if subcode.tag == 'DepartmentSale':
            #     if int(subcode.attrib.get('QtyIsWeight')):
            #         qty = 1
            #         weight = int(subcode.attrib.get('Qty'))
            #     else:
            #         qty = int(subcode.attrib.get('Qty'))
            #         weight = 0
            #
            #     child_sales.append({
            #         'product': subcode.attrib.get('DepartmentNo'),
            #         'price': int(subcode.attrib.get('Price')),
            #         'amount': int(subcode.attrib.get('Amount')),
            #         'qty': qty,
            #         'weight': weight,
            #         'time': time(
            #             int(subcode.attrib.get('Time')[0:2]),
            #             int(subcode.attrib.get('Time')[3:5]),
            #             int(subcode.attrib.get('Time')[6:8])
            #         ),
            #         'ticket': int(subcode.attrib.get('TicketNumber')),
            #         'pos': int(subcode.attrib.get('PosNo')),
            #     })
            if subcode.tag == 'TicketTotal':
                if not int(subcode.attrib.get('VoidTicket')) and not int(subcode.attrib.get('SaveTicket')):
                    ticket_total += int(subcode.attrib.get('Amount', 0))
                    product_sales += child_sales

    return product_sales, ticket_total