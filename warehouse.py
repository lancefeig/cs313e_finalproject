
#wooooooo Ava's (probably) wrong and weird code!!
#Also I've never done partner coding so If I'm infringing on some sorta
#co-coding etiquette or code-y people rules I'm sorryyyyy

class OrderTracking:
    def __init__(self):
        self.order_records = [] #list of dictionaries

    def place_order(self, customer_details, chemical_list): #idk what should go in customer_details. Just name?
        new_order = {
            'order_id': len(self.order_records) + 1,
            'customer_details': customer_details,
            'chemical_list': chemical_list
        }
        self.order_records.append(new_order)
        self.order_records.sort(key=lambda x: x['order_id'])  #make sure the records are sorted by order ID for binary search

    def process_order_queue(self):#What are we supposed to DO with the processed order?
        if len(self.order_records) > 0: #check if empty
            processed_order = self.order_records.pop(0)#removes first one as processed
            print(f"Processing order {processed_order['order_id']} for {processed_order['customer_details']}")
        else:
            print("No orders to process.")

    def binary_search_order(self, order_id): #use binary search to find order number by order ID
        low, high = 0, len(self.order_records) - 1

        while low <= high:
            mid = (low + high) // 2
            mid_order_id = self.order_records[mid]['order_id']

            if mid_order_id == order_id:
                return self.order_records[mid]
            elif mid_order_id < order_id:
                low = mid + 1
            else:
                high = mid - 1

        return None