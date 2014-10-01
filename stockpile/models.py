from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String)
    sales = db.relationship("Sales", backref="department")
    items = db.relationship("Item", backref="department")

    def __init__(self, id, description):
        self.id = id
        self.description = description

    def __repr__(self):
        return '{name} ({id})'.format(id=self.id, name=self.description)


class Item(db.Model):
    __tablename__ = 'item'
    upc = db.Column(db.BigInteger, primary_key=True)
    description = db.Column(db.String(30))
    pack = db.Column(db.Float(1))
    size = db.Column(db.Float(2))
    uom = db.Column(db.String(10))
    vendor = db.Column(db.String(6))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    srp = db.Column(db.Float(2))
    base_cost = db.Column(db.Float(2))
    case_cost = db.Column(db.Float(2))
    vendor_item = db.Column(db.String(20))
    zoned = db.Column(db.String(1))
    date_created = db.Column(db.DateTime, default=datetime.now)

    @property
    def dict(self):
        item = {
            'upc': str(self.upc).zfill(13),
            'description': self.description,
            'pack': self.pack,
            'size': self.size,
            'uom': self.uom,
            'department': str(self.department),
            'department_id': self.department_id,
            'srp': self.srp,
        }
        return item

    @property
    def upc13(self):
        return str(self.upc).zfill(13)

    def recent_sales(self):
        s = Sales.query.filter_by(upc=str(self.upc).zfill(13)).order_by(Sales.date.desc())
        return s

    def update(self, description, pack, size, uom, vendor, department,
               srp, base_cost, case_cost, vendor_item, zoned):
        if self.description != description:
            self.description = description
        if self.pack != float(pack):
            self.pack = float(pack)
        if self.size != float(size):
            self.size = float(size)
        if self.uom != uom:
            self.uom = uom
        if self.vendor != vendor:
            self.vendor = vendor
        if self.department_id != int(department):
            self.department_id = int(department)
        if self.srp != float(srp):
            self.srp = float(srp)
        if self.base_cost != float(base_cost):
            self.base_cost = float(base_cost)
        if self.case_cost != float(case_cost):
            self.case_cost = float(case_cost)
        if self.vendor_item != vendor_item:
            self.vendor_item = vendor_item
        if self.zoned != zoned:
            self.zoned = zoned

    def __init__(self, upc, description, pack, size, uom, vendor, department,
                 srp, base_cost, case_cost, vendor_item, zoned):
        self.upc = upc
        self.description = description
        self.pack = int(pack)
        self.size = float(size)
        self.uom = uom
        self.vendor = vendor
        self.department_id = int(department)
        self.srp = float(srp)
        self.base_cost = base_cost
        self.case_cost = case_cost
        self.vendor_item = vendor_item
        self.zoned = zoned

    def __repr__(self):
        return '<{upc} - {description}'.format(upc=self.upc, description=self.description)


class Sales(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    store = db.Column(db.String)
    date = db.Column(db.Date)
    upc = db.Column(db.String)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    pack = db.Column(db.String)
    size = db.Column(db.String)
    mult = db.Column(db.Integer)
    srp = db.Column(db.Float(2))
    sales = db.Column(db.Float(2))
    quantity = db.Column(db.Float(2))
    costs = db.Column(db.Float(2))
    gm = db.Column(db.Float(2))
    description = db.Column(db.String(40))

    def get_margin(self):
        try:
            gm = (self.sales - self.costs) / self.sales * 100
            return gm
        except ZeroDivisionError:
            return 0

    def __init__(self, store, date, upc, department, pack, size, mult, srp, sales, costs, gm, description, quantity):
        self.store = store
        self.date = date
        self.upc = upc
        self.department_id = department
        self.pack = pack
        self.size = size
        self.mult = mult
        self.srp = srp
        self.sales = sales
        self.costs = costs
        self.gm = gm
        self.description = description
        self.quantity = quantity

    def __repr__(self):
        return "<Sale('%s','%s','%s')>" % (self.upc, self.sales, self.costs)


class StockPile(db.Model):
    __tablename__ = 'stockpile'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.BigInteger, db.ForeignKey('item.upc'))
    weight = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer)
    store = db.Column(db.Integer)
    type = db.Column(db.Integer) #1=Sale, 2=Adjustment, 3=Transfer, 4=Physical
    created = db.Column(db.DateTime)
    logged = db.Column(db.DateTime, default=datetime.now)
    reference = db.Column(db.String(200))
    identifier = db.Column(db.String(200))


class Physical(db.Model):
    """Stores physical inventory during bi-annual stock take."""
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.BigInteger, db.ForeignKey('item.upc'))
    scanned_upc = db.Column(db.String)
    decoded_upc = db.Column(db.String)
    quantity = db.Column(db.Float)
    store = db.Column(db.Integer)
    user = db.Column(db.String)
    created = db.Column(db.DateTime, default=datetime.now)
    flag = db.Column(db.Integer)
    item = db.relationship("Item", backref="physical", lazy='joined')

    def __init__(self, upc, quantity, store, user):
        item = Item.query.filter_by(upc=int(upc)).first()
        self.item = item
        self.scanned_upc = upc
        self.quantity = quantity
        self.store = store
        self.user = user

    def __repr__(self):
        return '{user}/{upc}/{store}/{quantity}'.format(
            user=self.user,
            quantity=self.quantity,
            store=self.store,
            upc=self.scanned_upc
        )