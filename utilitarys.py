import json
class Operador():
    def __init__(self,id,state='available'):
        self.id=id
        self.state=state  #available,ringing, busy
        self.historic_calls=dict()
        self.call_current=None
    def set_call_current(self,call):
        self.call_current=call
    def get_call_current(self):
        return self.call_current
    def set_state(self,state):
        self.state=state
    def get_state(self):
        return self.state
    
class Call():
    def __init__(self,id,op_current=None,state=None):
        self.id=id
        self.op_current=op_current
        self.state=state #waiting,finished,ringing,answering,#missed
    def set_op_current(self,op):
        self.op_current=op
    def get_op_current(self):
        return self.op_current
    def set_state(self,state):
        self.state=state
    def get_state(self):
        return self.state

class Queue(object):
    def __init__(self):
        self.dados = []
    def insere(self, elemento):
        self.dados.append(elemento)
    def retira(self):
        return self.dados.pop(0)
    def topo(self):
        return self.dados[0]
        
    def vazia(self):
        return len(self.dados) == 0


