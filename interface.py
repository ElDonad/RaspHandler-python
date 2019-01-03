from EventObj import EventObj

class Interface(EventObj):
    id = 'Interface'
    allowUserInteraction = False
    allowAiguillageHandling = False

    def __init__(self):
        super().__init__()
    def launch(self):
        pass

    def stop(self, message):
        pass

    def init(self):
        pass

    def save(self):
        return {
            'id':self.id,
            'allowUserInteraction':self.allowUserInteraction,
            'allowAiguillageHandling':self.allowAiguillageHandling
        }

    def restore(self, data):
        self.id = data['id']
        self.allowUserInteraction = data['allowUserInteraction']
        self.allowAiguillageHandling = data['allowAiguillageHandling']

    def onAiguillageSwitched(self, aiguillage):
        print("[INTERFACE]Aiguillage switched")
