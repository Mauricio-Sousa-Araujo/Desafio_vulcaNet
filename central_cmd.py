from cmd import Cmd
from utilitarys import Queue, Operador, Call

class Control (Cmd):
    def __init__(self):
        super().__init__()
        self.prompt= "->"
        self.ops=dict()
        self.historic_calls=dict()
        self.calls_queue=Queue()
        self.ops_ava=Queue()        #Operadores disponíveis

        #Configura dois operadores
        self.ops['A']=Operador('A')
        self.ops['B']=Operador('B')
        self.ops_ava.insere(self.ops['A'])
        self.ops_ava.insere(self.ops['B'])


    def do_call(self,id):
        '''
        Recebe uma chamada e verifica se existe algum operador disponível
        '''
        print(f'Call {id} received')
        self.historic_calls[id]=Call(id)                #Guardamos todas as chamadas
        self.delivering_call(self.historic_calls[id])

    def delivering_call(self,c):
        '''
        Verifica se algum operador está disponível e manda uma chamada para ele
        '''
        if(self.ops_ava.vazia()):
            print(f'Call {c.id} waiting in queue')
            self.calls_queue.insere(c)
            c.set_state('waiting')
        else: 
            op=self.ops_ava.retira()        #Pega um operador disponível
            print(f'Call {c.id} ringing for operator {op.id}')
            
            op.set_state('ringing')
            op.set_call_current(c)               #Seta a call corrente para o operador que está ringing
            op.historic_calls[c.id]=c

            c.set_state('ringing')
            c.set_op_current(op)
   
    def do_answer(self,id):
        #Call c.id answered by operator op.id
        op  = self.ops[id]
        op.set_state('busy')
        
        call=op.get_call_current()
        call.set_op_current(op)
        call.set_state('answering')
        print(f'Call {call.id} answered by operator {op.id}')

    def do_reject(self ,id ):
        op=self.ops[id]
        call=op.get_call_current()
        print(f'Call {call.id} rejected by operator {op.id}')
        self.calls_queue.insere(call)
        call.set_state('waiting')
        op.set_state('available')
        call.set_op_current(None)
        self.ops_ava.insere(op)

        self.routine_delivering()   #Verifica se existe uma chamada na fila para esse novo operados dispinível

    def do_hangup(self ,id ) :
        #Call 1 finished and operator A available
        #Call <call id> missed
        
        call=self.historic_calls[id]
        op=call.op_current
        if(call.get_state()=='answering'):
            print(f'Call {call.id} finished and operator {op.id} available')
            #Após finalizar a chamada, attualizamos o estado do operador
            op.set_state('available')
            self.ops_ava.insere(op)
            call.set_state('finished')

        else:
            print(f'Call {call.id} missed')
            call.set_state('missed')
            if(op):
                op.set_state('available')
                self.ops_ava.insere(op)
    
        self.routine_delivering()

    def routine_delivering(self):
        if((not self.calls_queue.vazia()) and  (not self.ops_ava.vazia()) ):
            call=self.calls_queue.retira()
            if(call.get_state()=='waiting'):
                self.delivering_call(call)
            else:
                self.routine_delivering() #Procura por uma chamada válida
          

    def do_createOp(self, id):
        new_op=Operador(id)
        self.ops[id]=new_op
        self.ops_ava.insere(new_op)

    def do_getOperador(self,aux):
        print(self.ops)

    def do_EOF(self, args):
        return True
      
if __name__ == '__main__':
    op=Control()
    op.cmdloop("loop starts. Press ^D to exit")
