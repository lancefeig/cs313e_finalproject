import os

HASH_TABLE_SIZE = 100
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
FILE_IN = "data.txt"
FILE_OUT = "data.txt"
PROPERTIES = ["molar mass", "density"]

class DataManager:
    def __init__(self, directory, file_in, file_out):
        self.data_path_in = os.path.join(directory, file_in)
        self.data_path_out = os.path.join(directory, file_out)
        self.inventory = Inventory()
        self.queue = OrderQueue(self.inventory)

    def data_in(self):
        try:
            with open(self.data_path_in,"r",encoding="utf-8") as file:
                n_chemicals = int(file.readline().strip)
                n_orders = int(file.readline().strip)
                #enter in n chemicals (each chemical takes up 2 lines: name & quantity, property values)
                for _ in range(n_chemicals*2):
                    attributes = file.readline().split()
                    name = ' '.join(attributes[0].split('_'))
                    quantity = float(attributes[1])
                    properties_lst = file.readline().split()
                    properties_dict = dict(zip(PROPERTIES, [float(x) for x in properties_lst]))
                    new = Chemical(name, quantity, properties_dict)
                    self.inventory.add_chemical(new)
                #enter in n_orders (each order takes up 3 lines: customer & order id, chemicals, quantities)
                for _ in range(n_orders*3):
                    attributes = file.readline().split()
                    customer = ' '.join(attributes[0].split('_'))
                    order_id = int(attributes[1])
                    chemicals_lst = file.readline().split()
                    quantities_lst = file.readline().split()
                    chemicals_dict = dict(zip(chemicals_lst, [float(x) for x in quantities_lst]))
                    self.queue.enqueue_order(order_id, customer, chemicals_dict)
        #catch error if data.txt does not exist
        except IOError:
            print("No data was found. Empty inventory initialized.")

    def data_out(self):
        with open(self.data_path_out,"w",encoding="utf-8") as file:
            pass

    def main_loop(self):
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

    def alphabetical_list(self):
        flat = []
        for row in self.hash_table:
            flat.extend(row)
        flat.sort(key=lambda x: x.name)
        return flat

class Chemical:
    def __init__(self, name, quantity, properties):
        self.name = name #string
        self.quantity = quantity #integer
        self.properties = properties #dictionary of chemical properties
        self.hash_key = name_to_key(name) #integer

class OrderQueue:
    def __init__(self, inventory):
        self.inventory = inventory
        self.order_queue = [] #list of dictionaries

    def enqueue_order(self, order_id, customer, chemicals_dict):
        new_order = {
            'order_id': order_id,
            'customer': customer,
            'chemicals_dict': chemicals_dict
        }
        self.order_queue.append(new_order)

    def process_order(self):

        if not self.order_queue: #if order_queue empty
            print("No orders to process.")
            return

        current_order = self.order_queue.pop(0) #dequeue order from front, assign to current_order
        print(f"Processing order {current_order['order_id']} for {current_order['customer']}")

        order_copy = current_order['chemicals_dict'].copy()  # Create a copy of the original order

        for chemical, desired_quantity in current_order['chemicals_dict'].items(): #start iterating
            chemical_obj = self.inventory.find_chemical(chemical)
            if chemical_obj is None:
                ignore_fill = input(f"Chemical {chemical} does not exist. Ignore and fill? (y/n): ").lower()
                if ignore_fill == 'y': #still want the order
                    print(f"Ignoring {chemical}.")
                    del order_copy[chemical]  # Remove the chemical from the copy of the order
                else: #don't ignore and fill
                    self.order_queue.append(current_order)
                    print("Order added back to the queue.") #can change the message here
                    return #end bc now its at the back of the queue

            elif chemical_obj.quantity < desired_quantity: #insufficient quantity
                ignore_quantity = input(f"Available quantity of {chemical} is too low. Ignore and fill? (y/n): ").lower()
                if ignore_quantity == 'y': #still want the order
                    print(f"{chemical}: Instead of {desired_quantity}, you will receive {chemical_obj.quantity}.")
                    order_copy[chemical] = chemical_obj.quantity  #change the desired quantity to available quantity
                else:#don't ignore and fill
                    self.order_queue.append(current_order)
                    print("Order added back to the queue.")
                    return #end bc now its at the back of the queue

        for chemical, desired_quantity in order_copy.items():#look through the copy
             # Use update_chemical to check and update the quantities
            self.inventory.update_chemical(chemical, -desired_quantity) #will catch if less than 0

        print("Order successfully processed and chemicals filled.")

def name_to_key(string):
    #hash key based on the sum of the ASCII numbers
    return sum(list(map(lambda i: ord(i), string))) % HASH_TABLE_SIZE

if __name__ == "__main__":
    the_warehouse = DataManager(DIRECTORY, FILE_IN, FILE_OUT)
    the_warehouse.data_in()
    the_warehouse.main_loop()
