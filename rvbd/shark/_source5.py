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
            self.api.update(self.id, self.data)

    @s4.Interface4.name.setter
    def name(self, value):
        self.data.name = value
