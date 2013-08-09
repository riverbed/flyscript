from rvbd.shark import _source4 as s4

class Job5(s4.Job4):
    pass

class Interface5(s4.Interface4):    

    def save(self):
        if self.shark.model == "vShark":
            self.api.update(self.id, {
                    'name': self.data.name,
                    'description': self.data.description
                    })
        else:
            # we are in a normal shark, we have to
            # delete things we cannot modify
            data = self.data.copy()
            del data['interface_components']
            del data['link']
            del data['board']
            del data['is_promiscuous_mode']
            del data['type']
            del data['id']
            self.api.update(self.id, data)
        self.update()

    @s4.Interface4.name.setter
    def name(self, value):
        self.data.name = value
