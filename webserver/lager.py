class Produkt:
    def __init__(self, namn, vikt):
        self.namn = namn
        self.vikt = vikt

    def getWeight(self):
        return self.vikt

class Order:
    def __init__(self, lists, adress, ordernumber, qr_code_filename=None):
        self.lists = lists
        self.adress = adress
        self.ordernumber = ordernumber
        self.qr_code_filename = qr_code_filename 

    def getOrderNmbr(self):
        return self.ordernumber

    def getTotWeight(self):
        tot = 0
        for p in self.lists:
            tot += p.getWeight()
        return tot
    #La till get adress för att få korrekt adress
    def getAdress(self):
        return self.adress

    def wievInfo(self):
        return f"Produkt: {self.lists}, \n Adress: {self.adress}"
    
    def set_qr_code(self, filename):
        self.qr_code_filename = filename

    def get_qr_code(self):
        return self.qr_code_filename

class Test:
    def __init__(self, orderlist):
        self.orderlist = orderlist

    #La till isInstanceOf för att säkerställa att n skickas som en order och inte any
    def getOrder(self, ordernbr):
        for n in self.orderlist:
            if isinstance(n, Order) and n.getOrderNmbr() == ordernbr:
                return n
        return None
