import os
import time

HASH_TABLE_SIZE = 100
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
FILE_IN = "data.txt"
FILE_OUT = "data.txt"
PROPERTIES = ["molar mass", "density"]
PROPERTIES_UNITS = ["g/mol", "kg/m^3"]
MENU = """------------------------------------------
Please enter an option:
Add a Chemical (a)
Remove a Chemical (r)
Update a Quantity (u)
Create an Order (c)
Process an Order (p)
Display Inventory Based on Quantity (q)
Display Inventory Based Alphabetically (d)
Exit the Warehouse (e)
------------------------------------------\n"""

class DataManager:
    def __init__(self, directory, file_in, file_out):
        self.data_path_in = os.path.join(directory, file_in)
        self.data_path_out = os.path.join(directory, file_out)
        self.inventory = Inventory()
        self.queue = OrderQueue(self.inventory)
        self.quantities = QuantityChecker(self.inventory)

    def data_in(self):
        try:
            with open(self.data_path_in, "r", encoding="utf-8") as file:
                n_chemicals = int(file.readline().strip())
                n_orders = int(file.readline().strip())
                #enter in n chemicals (each chemical takes up 2 lines: name & quantity, property values)
                for _ in range(n_chemicals):
                    attributes = file.readline().split()
                    name = attributes[0].replace('_', ' ').lower()
                    quantity = round(float(attributes[1]), 2)
                    properties_lst = list(map(lambda x: x.replace('_', ' '), file.readline().split()))
                    properties_dict = dict(zip(PROPERTIES, properties_lst))
                    new = Chemical(name, quantity, properties_dict)
                    self.inventory.add_chemical(new)
                #enter in n_orders (each order takes up 3 lines: customer & order id, chemicals, quantities)
                for _ in range(n_orders):
                    attributes = file.readline().split()
                    customer = attributes[0].replace('_', ' ').title()
                    order_id = int(attributes[1])
                    chemicals_lst = list(map(lambda x: x.replace('_', ' '), file.readline().split()))
                    quantities_lst = file.readline().split()
                    chemicals_dict = dict(zip(chemicals_lst, [round(float(x), 2) for x in quantities_lst]))
                    self.queue.enqueue_order(order_id, customer, chemicals_dict)
        #catch error if data.txt does not exist
        except IOError:
            print("No data was found. Empty inventory initialized.\n")

    def data_out(self):
        with open(self.data_path_out, "w", encoding="utf-8") as file:
            file.write(f"{self.inventory.n}\n{len(self.queue.order_queue)}")
            for chemical in self.inventory.alphabetical_list():
                name = chemical.name.replace(' ', '_').lower()
                quantity = round(chemical.quantity, 2)
                properties = list(map(lambda x: f"{x.replace(' ', '_')} ", chemical.properties.values()))
                file.write(f"\n{name} {quantity}\n")
                file.writelines(properties)
            for order in self.queue.order_queue:
                customer = order['customer'].replace(' ', '_').title()
                order_id = order['order_id']
                chemicals_lst = list(map(lambda x: f"{x.replace(' ', '_')} ", order['chemicals_dict'].keys()))
                quantities_lst = list(map(lambda x: f"{x} ", order['chemicals_dict'].values()))
                file.write(f"\n{customer} {order_id}\n")
                file.writelines(chemicals_lst)
                file.write('\n')
                file.writelines(quantities_lst)

    def main_loop(self):
        self.data_in()

        while True:
            choice = input(MENU).strip().lower()
            print()

            match choice:
                # Add a Chemical
                case 'a':
                    name = input("Please enter the new chemical name:\n").strip().lower()
                    quantity = round(float(input("Please enter the new chemical quantity in kg:\n")), 2)
                    properties_lst = []

                    for i, prop in enumerate(PROPERTIES):
                        print(f"Please enter the {prop} in {PROPERTIES_UNITS[i]}:")
                        properties_lst.append(input())

                    properties_dict = dict(zip(PROPERTIES, properties_lst))
                    new = Chemical(name, quantity, properties_dict)
                    self.inventory.add_chemical(new)
                # Remove a Chemical
                case 'r':
                    name = input("Please enter the chemical name to be removed:\n").strip().lower()
                    self.inventory.remove_chemical(name)
                # Update a Quantity
                case 'u':
                    name = input("Please enter the chemical name to be updated:\n").strip().lower()
                    change = round(float(input("Please enter the change in quantity in kg:\n")),2)
                    self.inventory.update_chemical(name, change)
                # Create an Order
                case 'c':
                    order_id = time.strftime("%Y%m%d%H%M%S", time.gmtime())
                    customer = input("Please enter the name of the customer:\n").strip().title()
                    chemicals_lst, quantities_lst = [], []
                    for i in range(int(input("Please enter the number of desired chemicals:\n"))):
                        chemicals_lst.append(input(f"Please enter the name of chemical #{i+1}:\n").strip().lower())
                        quantities_lst.append(round(float(input(f"Please enter the quantity of chemical #{i+1}:\n")), 2))
                    chemicals_dict = dict(zip(chemicals_lst, quantities_lst))
                    self.queue.enqueue_order(order_id, customer, chemicals_dict)
                # Process an Order
                case 'p':
                    self.queue.process_order()
                # Display Inventory Based on Quantity
                case 'q':
                    quantity = round(float(input("What quantity do you want cut off the inventory display at?:\n")), 2)
                    above_or_below = input("Would you like to display above or below (a/b):\n").strip().lower()
                    index, sorted_lst = self.quantities.binary_search(quantity)

                    if above_or_below == 'a':
                        obj_range = sorted_lst[index:]
                    else:
                        obj_range = sorted_lst[:index]

                    for obj in obj_range:
                        print(obj)
                    print()
                # Display Inventory Based Alphabetically
                case 'd':
                    flat = self.inventory.alphabetical_list()
                    for obj in flat:
                        print(obj)
                    print()
                # Exit the Warehouse
                case 'e':
                    break
                case _:
                    print("Please enter a valid option.\n")

            self.data_out()

            for i in range(1,4):
                time.sleep(0.5)
                print('.'*i)
                time.sleep(0.5)
            print()

        self.data_out()
        print("Inventory and pending orders have been saved.\n")

class Inventory:
    def __init__(self):
        self.hash_table = [[] for x in range(HASH_TABLE_SIZE)] #empty 2-D array
        self.n = 0

    def add_chemical(self, obj):
        if self.find_chemical(obj.name) is None:
            self.hash_table[obj.hash_key].append(obj)
            self.n += 1
            print(f"{obj.name} sucessfully added.\n")
            return
        print("Sorry, this chemical is already in the inventory. Please update the quantity instead.\n")

    def remove_chemical(self, name):
        obj = self.find_chemical(name)
        if obj is not None:
            self.hash_table[obj.hash_key].remove(obj)
            self.n -= 1
            print(f"{obj.name} sucessfully removed.\n")
            return
        print("Sorry, this chemical is not in the inventory\n")

    def update_chemical(self, name, change):
        obj = self.find_chemical(name)
        if obj is not None:
            if obj.quantity + change > 0:
                obj.quantity += change
                print(f"{obj.name} sucessfully updated from '{obj.quantity - change}' to '{obj.quantity}' kg.",end='\n')
                return
            print("Chemical quantity with applied change is less than zero.\n")
            return
        print("Sorry, this chemical is not in the inventory.\n")

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
        #sorts flattened hash table by alphabetical order
        flat.sort(key=lambda x: x.name)
        return flat

    #################AVA ADDED THIS to work with quantity checker##################
    def quantity_sorted_list(self):
        # Returns a list of all chemicals sorted by quantity in ascending order
        flat = []
        for row in self.hash_table:
            flat.extend(row)
        # Sorts flattened hash table by quantity
        flat.sort(key=lambda x: x.quantity)
        return flat

class Chemical:
    def __init__(self, name, quantity, properties):
        self.name = name #string
        self.quantity = quantity #integer
        self.properties = properties #dictionary of chemical properties
        self.hash_key = name_to_key(name) #integer

    def __str__(self):
        print_form = []
        print_form.append(f"Name: {self.name}")
        print_form.append(f"    Quantity: {self.quantity} kg")
        #format and print properties
        properties_list = list(map(lambda key, units: f"    {key.title()}: {self.properties[key]} {units}", self.properties.keys(), PROPERTIES_UNITS))
        print_form.extend(properties_list)
        return '\n'.join(print_form)

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
        print(f"Order #{new_order['order_id']} for {new_order['customer']} sucessfully queued.\n")

    def process_order(self):
        if not self.order_queue: #if order_queue empty
            print("No orders to process.\n")
            return

        current_order = self.order_queue.pop(0) #dequeue order from front, assign to current_order
        print(f"Processing order #{current_order['order_id']} for {current_order['customer']}:\n")

        order_copy = current_order['chemicals_dict'].copy()  # Create a copy of the original order

        for chemical, desired_quantity in current_order['chemicals_dict'].items(): #start iterating
            chemical_obj = self.inventory.find_chemical(chemical)
            if chemical_obj is None:
                ignore_fill = input(f"Chemical {chemical} is not in the inventoru. Ignore and fill rest of the order? (y/n):\n").lower()
                if ignore_fill == 'y': #still want the order
                    print(f"Ignoring {chemical}.\n")
                    del order_copy[chemical]  # Remove the chemical from the copy of the order
                else: #don't ignore and fill
                    self.order_queue.append(current_order)
                    print("Order added back to the queue.\n") #can change the message here
                    return #end bc now its at the back of the queue

            elif chemical_obj.quantity < desired_quantity: #insufficient quantity
                ignore_quantity = input(f"Available quantity of {chemical} is too low. Ignore and fill available kilograms? (y/n):\n").lower()
                if ignore_quantity == 'y': #still want the order
                    print(f"For {chemical}, instead of {desired_quantity} kg, you will receive {chemical_obj.quantity} kg.\n")
                    order_copy[chemical] = chemical_obj.quantity  #change the desired quantity to available quantity
                else:#don't ignore and fill
                    self.order_queue.append(current_order)
                    print("Order added back to the queue.\n")
                    return #end bc now its at the back of the queue

        for chemical, desired_quantity in order_copy.items():#look through the copy
             # Use update_chemical to check and update the quantities
            self.inventory.update_chemical(chemical, -desired_quantity) #will catch if less than 0

        print(f"Order successfully processed and {len(order_copy)} chemicals filled.\n")

class QuantityChecker:
    def __init__(self, inventory):
        self.inventory = inventory
        self.sorted_chemicals = inventory.quantity_sorted_list()

    def binary_search(self, number):
        self.sorted_chemicals = self.inventory.quantity_sorted_list()
        # Binary search for the index of the chemical closest to the given quantity
        low, high = 0, len(self.sorted_chemicals) - 1
        while low <= high:
            mid = (low + high) // 2
            mid_quantity = self.sorted_chemicals[mid].quantity
            if mid_quantity == number:
                return mid
            elif mid_quantity < number:
                low = mid + 1
            else:
                high = mid - 1
        # Return the index of the closest chemical (rounded up)
        index = low if low < len(self.sorted_chemicals) else len(self.sorted_chemicals) - 1
        return index, self.sorted_chemicals

def name_to_key(string):
    #hash key based on the sum of the ASCII numbers
    return sum(list(map(lambda i: ord(i), string))) % HASH_TABLE_SIZE

if __name__ == "__main__":
    the_warehouse = DataManager(DIRECTORY, FILE_IN, FILE_OUT)
    the_warehouse.main_loop()
