from twisted.internet.protocol import Factory
from twisted.internet import reactor, protocol, endpoints
from utilitarys import *
from twisted.protocols import basic
from twisted.internet import stdio
from cmd import Cmd

class QuoteProtocol(basic.LineReceiver):
    def __init__(self, factory=None):
        from os import linesep as delimiter
        self.cmd=ControlSimple()
        self.factory = factory
        self.ops=dict()             #Operadores existentes
        self.historic_calls=dict()  #Histórico de chamadas
        self.calls_queue=Queue()     #Chamadas em espera
        self.ops_ava=Queue()         #Operadores available
        
        
        
        self.treat={'call'  :   self.call,
                    'answer':   self.answer,
                    'reject':   self.reject,
                    'hangup':   self.hangup    
                        }

        
        self.ops['A']=Operador('A')
        self.ops['B']=Operador('B')
        self.ops_ava.insere(self.ops['A'])
        self.ops_ava.insere(self.ops['B'])

    def dataReceived(self, data):
        data=self.cmd.onecmd(data.decode("utf-8"))
        data=json.loads(data.decode("utf-8"))
        self.treat[data['command']](data['id']) #Chama a theread
        
    def call(self,id):
        reactor.callLater(10, self.timeout_call,id) #Timeout
        msg=f'Call {id} received\n'.encode('utf-8')
        print(msg)

        self.transport.write(msg)
        self.historic_calls[id]=Call(id)                #Guardamos todas as chamadas
        self.delivering_call(self.historic_calls[id])
        
    def delivering_call(self,c):
        if(self.ops_ava.vazia()):
            msg=f'Call {c.id} waiting in queue'.encode('utf-8')
            print(msg)
            self.transport.write(msg)
            self.calls_queue.insere(c)
            c.set_state('waiting')
        else: 
            op=self.ops_ava.retira()
            msg=f'Call {c.id} ringing for operator {op.id}'.encode('utf-8')
            print(msg)
            self.transport.write(msg)

            op.set_state('ringing')
            op.set_call_current(c)        #Seta a call corrente para o operador que está ringing
            op.historic_calls[c.id]=c

            c.set_state('ringing')  
            c.set_op_current(op)
   
    def timeout_call(self,id):
        call=self.historic_calls[id]
        if(call.get_state() == 'ringing'):
            op=call.get_op_current()
            msg=f'Call {call.id} ignored by operator {op.id}'.encode('utf-8')
            print(msg)
            self.transport.write(msg)
            op.set_state('available')
            self.ops_ava.insere(op)
            
    def answer(self,id):
        #Call c.id answered by operator op.id
        op  = self.ops[id]
        op.set_state('busy')
        call=op.call_current
        call.op_current=op
        call.state='answering'
        msg=f'Call {call.id} answered by operator {op.id}'.encode('utf-8')
        print(msg)
        self.transport.write(msg)

    def reject(self,id):
        op=self.ops[id]
        call=op.get_call_current()
        msg=f'Call {call.id} rejected by operator {op.id}'.encode('utf-8')
        print(msg)
        self.transport.write(msg)
        self.calls_queue.insere(call)
        call.set_state('waiting')
        op.set_state('available')
        call.set_op_current(None)
        self.ops_ava.insere(op)

        self.routine_delivering()

    def hangup(self,id):
        #Call 1 finished and operator A available
        #Call <call id> missed
        
        call=self.historic_calls[id]
        op=call.get_op_current()
        if(call.get_state()=='answering'):
            msg=f'Call {call.id} finished and operator {op.id} available'.encode('utf-8')
            print(msg)
            self.transport.write(msg)
            #Após finalizar a chamada, attualizamos o estado do operador
            op.set_state('available')
            self.ops_ava.insere(op)
            call.set_state('finished')
        else:
            msg=f'Call {call.id} missed'.encode('utf-8')
            self.transport.write(msg)
            call.set_state('missed')
            if(op):
                op.set_state('available')
                self.ops_ava.insere(op)
        
        self.routine_delivering()

    def routine_delivering(self):
        if((not self.calls_queue.vazia()) and  (not self.ops_ava.vazia()) ):
            call=self.calls_queue.retira()
            if(call.get_state()!='missed'):
                self.delivering_call(call)
            else:
                self.routine_delivering() #Procura por uma chamada válida
    
    
          
class QuoteFactory(protocol.ServerFactory):
    def __init__(self, quote=None):
        self.quote = quote 
    def buildProtocol(self, addr):
        return QuoteProtocol(self)

class ControlSimple (Cmd):
    def __init__(self):
        super().__init__()   
        self.prompt= "->"

    def do_call(self,id):
        return json.dumps({'command':'call','id':id}).encode('utf-8')
    def do_answer(self,id):
        return json.dumps({'command':'answer','id':id}).encode('utf-8')
    def do_reject(self ,id ):
        return json.dumps({'command':'reject','id':id}).encode('utf-8')
    def do_hangup(self ,id ):
        return json.dumps({'command':'hangup','id':id}).encode('utf-8')

    def do_EOF(self, args):
        return True




if __name__ == '__main__':
    #a = endpoints.serverFromString(reactor, "tcp:8000")
    #prot=QuoteFactory()
    #a.listen(prot)
    stdio.StandardIO(QuoteProtocol())
    #reactor.listenTCP(8000, QuoteFactory())
    reactor.run()

