#book data structure
class Book(object):
	#book constructor
    def __init__(self, item_number, stock, cost, type, title):
        self.item_number = item_number
        self.stock = stock
        self.cost = cost
        self.type = type
        self.title = title
	#decrease number of book
    def decrease_stock(self):
        if self.stock == 0:
            return False
        self.stock -= 1
        return True
	#increase number of book
    def increase_stock(self):
        self.stock += 1
	#update cost of book
    def update_cost(self, cost):
        self.cost = cost
	#get book's detail information
    def get_info(self):
        return {'item_number':self.item_number, 'stock':self.stock, 'cost':self.cost
                , 'type':self.type, 'title':self.title}
	#get book title and item number (for search request)
    def get_title(self):
        return {'item_number':self.item_number, 'title':self.title}