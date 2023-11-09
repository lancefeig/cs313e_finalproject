import os

HASH_TABLE_SIZE = 100
#saves pathway of this warehouse.py
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class DataManager:
    def __init__(self):
        #generates pathway of data.txt
        self.data_path = os.path.join(DIRECTORY,"data.txt")
        self.inventory = Inventory()
        self.queue = OrderQueue()

    def data_in(self):
        try:
            with open(self.data_path,"r",encoding="utf-8") as file:
                n_chemicals = int(file.readline().strip)
                n_orders = int(file.readline().strip)
                properties_lst = file.readline().split()
                #enter in n chemicals
                for _ in range(n_chemicals):
                    attributes = file.readline().split()
                    # pop chemmical name and quantity
                    name = attributes.pop(0)
                    quantity = int(attributes.pop(0))
                    properties = dict(zip(properties_lst, attributes))
                    new = Chemical(name, quantity, properties)
                    self.inventory.add_chemical(new)
                #enter in n_orders (each order takes up 3 lines: customer & order id, chemicals, quantities)
                for _ in range(n_orders*3):
                    attributes = file.readline().split()
                    customer = attributes[0]
                    order_id = attributes[1]
                    chemicals_lst = file.readline().split()
                    quantities_lst = [int(x) for x in file.readline().split()]
                    chemicals_dict = dict(zip(chemicals_lst, quantities_lst))
                    self.queue.enqueue_order(order_id, customer, chemicals_dict)
        #catch error if data.txt does not exist
        except IOError:
            print("No data was found. Empty inventory initialized.")

    def data_out(self):
        with open(self.data_path,"w",encoding="utf-8") as file:
            pass

    def interface(self):
        pass

class Inventory:
    def __init__(self):
        self.hash_table = [[]]*HASH_TABLE_SIZE #empty 2-D array
        self.n = 0

    def add_chemical(self, obj):
        if self.find_chemical(obj.name) is None:
            self.hash_table[obj.hash_key].append(obj)
            self.n += 1
        print("Sorry, this chemical is already in the inventory. Please update the quantity instead.")

    def remove_chemical(self, name):
        obj = self.find_chemical(name)
        if obj is not None:
            self.hash_table[obj.hash_key].remove(obj)
            self.n -= 1
        print("Sorry, this chemical is not in the inventory")

    def update_chemical(self, name, change):
        obj = self.find_chemical(name)
        if obj is not None:
            if obj.quantity + change > 0:
                obj.quantity += change
            raise ValueError("Chemical quantity with applied change is less than zero.")
        print("Sorry, this chemical is not in the inventory.")

    def print_chemical(self, obj):
        print(f"Name: {obj.name}")
        #format and print properties
        properties_list = list(map(lambda key: f"    {key.title()}: {obj.properties[key]}", obj.properties.keys()))
        print('\n'.join(properties_list))

    def find_chemical(self, name):
        hash_key = name_to_key(name)
        #check if bucket is empty
        if self.hash_table[hash_key] == []:
            return None
        #linearly probe for chemical name existing in bucket
        for curr in self.hash_table[hash_key]:
            if curr.name == name:
                return curr
        return None

class Chemical:
    def __init__(self, name, quantity, properties):
        self.name = name #string
        self.quantity = quantity #integer
        self.properties = properties #dictionary of chemical properties
        self.hash_key = name_to_key(name) #integer

def name_to_key(string):
    #hash key based on the sum of the ASCII numbers
    return sum(list(map(lambda i: ord(i), string))) % HASH_TABLE_SIZE

class OrderQueue:
    def __init__(self):
        self.order_queue = [] #list of dictionaries

    def enqueue_order(self, order_id, customer, chemicals_dict): #idk what should go in customer. Just name?
        new_order = {
            'order_id': order_id,
            'customer': customer,
            'chemicals_dict': chemicals_dict
        }
        self.order_queue.append(new_order)
        self.order_queue.sort(key=lambda x: x['order_id'])  #make sure the records are sorted by order ID for binary search

    def process_order_queue(self):#What are we supposed to DO with the processed order?
        if len(self.order_queue) > 0: #check if empty
            processed_order = self.order_queue.pop(0)#removes first one as processed
            print(f"Processing order {processed_order['order_id']} for {processed_order['customer']}")
        else:
            print("No orders to process.")

    def binary_search_order(self, order_id): #use binary search to find order number by order ID
        low, high = 0, len(self.order_queue) - 1

        while low <= high:
            mid = (low + high) // 2
            mid_order_id = self.order_queue[mid]['order_id']

            if mid_order_id == order_id:
                return self.order_queue[mid]
            elif mid_order_id < order_id:
                low = mid + 1
            else:
                high = mid - 1

        return None

def main():
    pass

main()
