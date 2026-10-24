from MQTT_client import user, device, dataPoint

class user_gui_object:
    def __init__(self, name):
        self.name = name
        self.devices = dict()        
        

class device_gui_object:
    def __init__(self, name):
        self.name = name
        self.data = dict()

class data_graph_object:
    def __init__(self, name):
        self.name = name
        self.values = []
    
    