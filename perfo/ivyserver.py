from ivy.std_api import *
import time
from ivy.ivy import IvyServer
import re
from abc import ABC, abstractmethod

# Define constants
ALTITUDE_THRESHOLD = 5001
READY_MESSAGE = "Ready"

class MessageContext:
    def __init__(self, IvyServer, agent, args):
        self.IvyServer=IvyServer
        self.agent = agent
        self.args = args
        
class MessageInterpreter(ABC):
    @abstractmethod
    def interpret_message(self, context):
        pass

    def extract_values(self, context, pattern):
        match = re.search(pattern, context.args[0])
        if match:
            return match.group(1)
        else:
            # print(f"Pattern {pattern} not found in {context.args[0]}")
            return None

class PerfoMessageInterpreter(MessageInterpreter):
    def interpret_message(self, context):
        print(f"{context.IvyServer.agent_name} received message from {context.agent.agent_name}: {context.args}")
        new_values = {}
        for key, pattern in context.IvyServer.regex_to_extract.items():
            value = self.extract_values(context, pattern)
            if value:
                new_values[key] = value
        if new_values:
            print("Old Stored values:", context.IvyServer.stored_values)
            print("New values:", new_values)
            context.IvyServer.stored_values.update(new_values)
            print("New Stored values:", context.IvyServer.stored_values)

class IHMMessageInterpreter(MessageInterpreter):
    def interpret_message(self, context):
        print(f"{context.IvyServer.agent_name} received message from {context.agent.agent_name}: {context.args}")
        altitude_value = self.extract_values(context, r"Altitude=(\d+)")
        if altitude_value:
            print("Altitude value:", altitude_value)
            if int(altitude_value)>ALTITUDE_THRESHOLD:context.IvyServer.authorizeConfig=False    
            else:context.IvyServer.authorizeConfig=True
            print("authorizeConfig : ", context.IvyServer.authorizeConfig)

class Server:
    def __init__(self, agent_name, bus_address, subscriptions=[], regex_to_extract={}, message_interpreter=None, authorizeConfig=None):
        self.agent_name = agent_name
        self.bus_address = bus_address
        self.subscriptions = subscriptions
        self.regex_to_extract = regex_to_extract
        self.message_interpreter = message_interpreter
        self.authorizeConfig = authorizeConfig
        self.stored_values = {}
        self.IvyServer = None
        
    def app_callback(self, agent, event):
        if event == IvyApplicationConnected:
            print(f"Application {agent} connected")
        elif event == IvyApplicationDisconnected:
            print(f"Application {agent} disconnected")
            
    def die_callback(self, agent, msg_id):
        print(f"Received DIE message from {agent}, msg_id: {msg_id}")   

    def run(self):
        try:
            self.IvyServer = IvyServer(self.agent_name, READY_MESSAGE, self.app_callback, self.die_callback)       
            self.IvyServer.start(self.bus_address)
            if self.subscriptions:
                for subscription in self.subscriptions:
                    self.IvyServer.bind_msg(self.on_message, subscription)
            self.show_status()
        except Exception as e:
            print(f"Failed to start server: {e}")
            
    def start_loop(self):
        while True:
            time.sleep(0.1)

    def stop(self):
        if self.IvyServer:
            self.IvyServer.stop()
        else:
            print("Failed to stop server: IvyServer is None")
        
    def show_status(self):
        print("----Status----")
        print("IvyServer : ", self.IvyServer)
        print("IvyServer.agent_name : ", self.IvyServer.agent_name)
        print("IvyServer.ready_message : ", self.IvyServer.ready_message)
        print("ip:port : ", self.bus_address)
        if not self.subscriptions:
            print("subscriptions : None")
        else:
            print("subscriptions : ", self.subscriptions)
        print("--------------")

    def send_message(self, message):
        if self.IvyServer is not None:
            self.IvyServer.send_msg(message)
        else:
            print("IvyServer is none")
            print("The following message couldn't be sent : ", message)

    def on_message(self, agent=None, *args):
        if agent is not None and self.message_interpreter is not None:
            context=MessageContext(self, agent, args)
            self.message_interpreter.interpret_message(context)
        else:
            self.stored_values = None
