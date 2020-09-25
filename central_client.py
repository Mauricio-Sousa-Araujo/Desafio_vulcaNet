from twisted.internet.protocol import Factory
from twisted.internet import reactor, protocol
from twisted.protocols import basic
from utilitarys import *
from cmd import Cmd

 
class QuoteProtocol(basic.LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        #self.cmd=Control(self)

    def connectionMade(self):
        print('Connecting')
    def dataReceived(self, data):
        print (data.decode('utf-8'))
        #self.transport.loseConnection()

class QuoteClientFactory(protocol.ClientFactory):
    def __init__(self):
        self.pt=QuoteProtocol(self)

    def buildProtocol(self, addr):
        return self.pt
    def clientConnectionFailed(self, connector, reason):
        print ('connection failed:', reason.getErrorMessage())
    def clientConnectionLost(self, connector, reason):
        print ('connection lost:', reason.getErrorMessage())

###Controle
class Control (Cmd):
    def __init__(self,protocol=None):
        super().__init__()   
        self.ops=dict()
        self.historic_calls=dict()
        self.calls_queue=Queue()
        self.ops_ava=Queue()
        self.protocol=protocol
        self.prompt= "->"

    def do_call(self,id):
        quote=json.dumps({'command':'call','id':id}).encode('utf-8')
        self.protocol.sendLine(quote)
    def do_answer(self,id):
        quote=json.dumps({'command':'answer','id':id}).encode('utf-8')
        self.protocol.sendLine(quote)
    def do_reject(self ,id ):
        quote=json.dumps({'command':'reject','id':id}).encode('utf-8')
        self.protocol.sendLine(quote)
    def do_hangup(self ,id ):
        quote=json.dumps({'command':'hangup','id':id}).encode('utf-8')
        self.protocol.sendLine(quote)

    def do_EOF(self, args):
        return True

if __name__ == '__main__':
    factory=QuoteClientFactory()
    control=Control(factory.pt)
    reactor.callInThread(control.cmdloop, b"loop starts. Press ^D to exit")
    localhost='127.0.0.1'
    reactor.connectTCP(localhost, 5678,factory )
    reactor.run()

    #line= 'call 1'
    #op.onecmd(line)
    
