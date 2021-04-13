#book data structure
class Book(object):
	#book constructor
	def __init__(self, item_number, stock, cost, type, title):
		self.item_number = item_number #item number of a book
		self.stock = int(stock) #remaining stock of the book
		self.cost = cost #Cost of the book
		self.type = type #type of the book
		self.title = title #book title
	#decrease number of book
	def update_stock(self, stock):
		self.stock += stock
		if(self.stock < 0):
			self.stock = 0
			return False
		else:
			return True
	
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