import os

HASH_TABLE_SIZE = 100
DIRECTORY = os.path.dirname(os.path.abspath(__file__)) #saves pathway of this warehouse.py

class FileManager:
    def __init__(self):
        self.data_path = os.path.join(DIRECTORY,"data.txt") #generates pathway of data.txt

    def data_in(self):
        pass

    def data_out(self):
        pass

class Inventory:
    def __init__(self):
        self.hash_table = [[]]*HASH_TABLE_SIZE #empty 2-D array

    def add_chemical(self, obj):
        if self.find_chemical(obj.name) is None:
            self.hash_table[obj.hash_key].append(obj)
        print("Sorry, this chemical is already in the inventory. Please update the quantity instead.")

    def remove_chemical(self, name):
        obj = self.find_chemical(name)
        if obj is not None:
            self.hash_table[obj.hash_key].remove(obj)
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

        if self.hash_table[hash_key] == []: #check if bucket is empty
            return None
        for curr in self.hash_table[hash_key]: #linearly probe for chemical name existing in bucket
            if curr.name == name:
                return curr
        return None

class Chemical:
    def __init__(self, name, properties, quantity=0):
        self.name = name #string
        self.properties = properties #dictionary of chemical properties
        self.quantity = quantity #integer
        self.hash_key = name_to_key(name) #integer

def name_to_key(string):
    #hash key based on the sum of the ASCII numbers
    return sum(list(map(lambda i: ord(i), string))) % HASH_TABLE_SIZE


#wooooooo Ava's (probably) wrong and weird code!!
#Also I've never done partner coding so If I'm infringing on some sorta
#co-coding etiquette or code-y people rules I'm sorryyyyy
class OrderTracking:
    def __init__(self):
        self.order_queue = [] #list of dictionaries

    def enqueue_order(self, customer_details, chemical_list): #idk what should go in customer_details. Just name?
        new_order = {
            'order_id': len(self.order_queue) + 1,
            'customer_details': customer_details,
            'chemical_list': chemical_list
        }
        self.order_queue.append(new_order)
        self.order_queue.sort(key=lambda x: x['order_id'])  #make sure the records are sorted by order ID for binary search

    def process_order_queue(self):#What are we supposed to DO with the processed order?
        if len(self.order_queue) > 0: #check if empty
            processed_order = self.order_queue.pop(0)#removes first one as processed
            print(f"Processing order {processed_order['order_id']} for {processed_order['customer_details']}")
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
