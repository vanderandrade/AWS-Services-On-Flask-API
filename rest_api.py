import json
from flask import Flask, jsonify
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

friends = {}

def setFriends(database):
    global friends
    friends = database

def addFriend(name: str) -> dict:
    global friends
    friend = {'name': name, 'owes': {}, 'owed_by': {}, 'balance': 0.0}
    friends['users'].append(friend)

    return friend

def getFriends(list_names: list) -> dict:
    return [f for f in friends['users'] if f['name'] in list_names]

def getAmount(friend: dict, friend_name: str, list_name: str) -> float:
    if not (friend_name) in friend.get(list_name):
        return 0.0
    return friend.get(list_name)[friend_name]

def getRecalculatedBalance(friend: dict) -> float:
    balance = 0.0

    balance -= sum(friend['owes'].values())
    balance += sum(friend['owed_by'].values())

    return balance

def addAmount(friend: dict, friend_name: str, main_list_name: str, secondary_list_name: str, amount: float):
    friend_amount = getAmount(friend, friend_name, secondary_list_name)

    if friend_amount > 0:
        if friend_amount < amount:
            friend.get(secondary_list_name).pop(friend_name)
            addAmount(friend, friend_name, main_list_name, secondary_list_name, amount - friend_amount)

            return
        if friend_amount == amount:
            friend.get(secondary_list_name).pop(friend_name)
            friend['balance'] = getRecalculatedBalance(friend)

            return
        else:
            friend_amount -= amount
            tmp = main_list_name
            main_list_name = secondary_list_name
            secondary_list_name = tmp
    else:
        friend_amount = amount

    if not (friend_name) in friend.get(main_list_name):
        friend.get(main_list_name)[friend_name] = 0.0
    friend.get(main_list_name)[friend_name] = friend_amount
    friend['balance'] = getRecalculatedBalance(friend)

def addIOU(iou: dict) -> list:
    involved = {}
    involved['users'] = []

    for friend in friends['users']:
        if friend.get('name') == iou['lender']:
            addAmount(friend, iou['borrower'], 'owed_by', 'owes', iou['amount'])
            involved['users'].append(friend)
        elif friend.get('name') == iou['borrower']:
            addAmount(friend, iou['lender'], 'owes', 'owed_by', iou['amount'])
            involved['users'].append(friend)

    #print(f'Involved: {involved}')
    return involved

class RestAPI:
    def __init__(self, database=None):
        setFriends(database)

    def get(self, url, payload=None):
        if payload is None:
            return json.dumps(friends)

        info = json.loads(payload)
        return json.dumps({'users': getFriends(info['users'])})

    def post(self, url, payload=None)-> object:
        if payload is None:
            raise Exception('Payload must have a value!')
        
        info = json.loads(payload)

        if url == '/add':
            new_friend = addFriend(info['user'])
            return json.dumps(new_friend)
        elif url == '/iou':
            iou = addIOU(info)
            return json.dumps(iou)

    def as_view(self):
        return self

api.add_resource(RestAPI, '/users', '/add', '/iou')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')