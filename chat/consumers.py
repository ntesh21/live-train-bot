# chat/consumers.py
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
import importlib

from chat.chatModel import learning2
#from chat.chatModel.restaurants.learning2 import welcome_msg
from chat.train_mode import check_train_mode,enter_train_mode
import subprocess

from subprocess import Popen
import os
lock=0
class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )


    # Receive message from room group
    def chat_message(self, event):
        global lock
        message = event['message']
        train_switch=check_train_mode(message)
        if train_switch== True or lock==1:
            print("training mode enabled")
            rep= (enter_train_mode(message))
            reply = ["<strong style='color:MediumSeaGreen;'>Training in progress...</strong>"]
            #print(rep)
            lock=rep[1]
            #print(lock)
            reply=rep[0]

        elif train_switch==False and lock==0:
            reply = str(learning2.response(message))
            #print(reply)

        elif train_switch==3:

            #stop model
            subprocess.check_call(["python3", "./chat/chatModel/model2.py"])
            reply = "<strong>Training in progress...</strong>"
            #modelreload
            importlib.reload(learning2)
            #print(os.system('./chat/chatModel/restaurants/model2.py'))

            reply="Training process finished.<br>Thank you for teaching me &#9757;.<br>Now you can ask me the query you trained me on."
            #Popen("./chat/chatModel/restaurants/model2.py")



        #welc_msg = welcome_msg

        print('hello:',reply)
        print('MSg',message)
        #print('Welcome', welc_msg)

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'reply':reply,
           # 'welc_msg': welc_msg
        }))


