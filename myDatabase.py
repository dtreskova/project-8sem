
import datetime

from peewee import *

from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel, QVariant

class MyModel(QAbstractTableModel):
    def __init__(self, items, labels):
        super().__init__()
        self.list = items.copy()
        self.colLabels = labels.copy()

    def rowCount(self, parent):
        return len(self.list)

    def columnCount(self, parent):
        return len(self.colLabels)
    
    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QVariant(self.colLabels[section])
        return QVariant()

    def data(self, index, role):
        if not index.isValid() or role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return QVariant()
        val = ''
        if role == QtCore.Qt.DisplayRole:
            try:
                tmp = self.list[index.row()]
                val = tuple(tmp)[index.column()]
            except IndexError:
                pass
        return val


mainDatabase = SqliteDatabase(None)

class BaseModel(Model):
    class Meta:
        database = mainDatabase

class Store(BaseModel):
    name = CharField()
    adress = CharField(unique = True)

class Product(BaseModel):
    name = CharField(unique = True)
    praise = IntegerField()
    store = ForeignKeyField(Store, null = True)

class Storage(BaseModel):
    adress = CharField(unique = True)
    product = ForeignKeyField(Product, backref="storage")

class Rate(BaseModel):
    author = CharField()
    stars = IntegerField()
    product = ForeignKeyField(Product)

class Supply(BaseModel):
    product = ForeignKeyField(Product)
    count = IntegerField()
    date = DateTimeField()

class Cashier(BaseModel):
    store = ForeignKeyField(Store)
    name = CharField(unique = True)
    salary = IntegerField()


#Заполним первый магазин
def initDatabase1():
    tmp_store = Store.create(name = "Store1", adress = "Lenina 1")
    tmp_product = Product.create(name = "product1", praise = 999999, store = tmp_store)
    tmp_storage = Storage.create(adress = "fantasy", product = tmp_product)
    tmp_supply = Supply.create(product = tmp_product, count = 1, date = datetime.datetime(2024, 10, 1, 12, 24))
    #tmp_supply = Supply.create(product = tmp_product, count = 111, date = datetime.datetime(2026, 10, 1, 12, 24))
    tmp_product = Product.create(name = "product2", praise = 100000*1000000, store = tmp_store)
    tmp_storage = Storage.create(adress = "Lenina 2", product = tmp_product)
    tmp_rate = Rate.create(author = "Petrov", stars = 3, product = tmp_product)
    tmp_supply = Supply.create(product = tmp_product, count = 33, date = datetime.datetime(1999, 10, 1, 12, 24))
    tmp_cash = Cashier.create(store = tmp_store, name = "Ivanov", salary = 10)

#Второй магазин
def initDatabase2():
    tmp_store = Store.create(name = "Store2", adress = "Lenina 3")
    tmp_product = Product.create(store = tmp_store, name = "product3", praise = 1970)
    tmp_storage = Storage.create(adress = "Lenina 4", product = tmp_product)
    tmp_rate = Rate.create(author = "Sidorov", stars = 0, product = tmp_product)
    tmp_supply = Supply.create(product = tmp_product, count = 10000000000, date = datetime.datetime(2021, 1, 1, 1, 0))
    tmp_cash = Cashier.create(store = tmp_store, name = "Ivanova", salary = 100000)

def initDatabase():
    initDatabase1()
    initDatabase2()

class MyDataBase:
    def __init__(self, name):
        mainDatabase.init(name)
        mainDatabase.connect()
        mainDatabase.create_tables([Store, Product, Storage, Rate, Supply, Cashier])
        try:
            initDatabase()
        except IntegrityError:
            print("database init canceled")


    def stores(self):
        return [i.name for i in Store.select()]

    def products(self):
        return [i.name for i in Product.select()]

    def products_in_supply(self):
        return {i.product.name : None for i in Supply.select()}.keys()

    def max_salary(self):
        return Cashier.select(fn.MAX(Cashier.salary)).scalar()

    def add(self, num, author, prod):
        finded = Product.get(Product.name == prod)
        if finded is None:
            return
        Rate.create(author = author, stars = num, product = finded)

    def first(self, name):
        tmp = [(str(i.date), i.count) for i in Supply.select().join(Product).where(Product.name == name)]
        #tmp.append(("all", Supply.select(fn.SUM(Supply.count)).join(Product).where(Product.name == name).scalar()))
        return MyModel(tmp, ["Дата поставки '"+name+"'", "количество"])

    def second(self, substr):
        tmp = [(i.adress, i.product.praise) for i in
               Storage.select().join(Product).join(Store).where(Store.name.contains(substr)).order_by(Product.praise)]
        return MyModel(tmp, ['адреса складов', 'цена'])

    def third(self, num, date):
        tmp = [(i.stars, i.product.name, i.product.store.adress) for i in
               Rate.select().join(Product).join(Supply).switch(Product).join(Store).join(Cashier).where((Supply.date > date) & (Cashier.salary < num))]
        return MyModel(tmp, ['рейтинг', 'товар', 'адрес'])
