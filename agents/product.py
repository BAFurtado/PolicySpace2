

class Product:
    def __init__(self, product_id, quantity, price):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def __repr__(self):
        return 'Product ID: %d, Quantity: %d, Price: %.1f' % (self.product_id, self.quantity, self.price)
