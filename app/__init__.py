from crypt import methods
from flask import Flask, json, request, send_file, send_from_directory
from config import app_config
import requests
import pandas as pd
import os.path
import base64
from io import BytesIO
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from itertools import groupby

def create_app(config_name):

    token = 'secret_GQmTn5J3kAJitkJXFAv2PJdbAVF2uut5sFweeE2MbOi'
    database = '93d86765d4414fb59077059a5ff895a4'

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Notion-Version": "2022-02-22",
        "Authorization": "Bearer " + token
    }

    app = Flask(__name__, instance_relative_config=True)
    #app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data')

    @app.route('/')
    def hello_world():
        return 'Hello Botion ! I am back with db running .......!'

    @app.route('/v1/notion/pages', methods=["POST"])
    def Notion_Create_Page():
        readURL = f"https://api.notion.com/v1/pages"

        NewPageData = {
            "parent": {"database_id": database},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": "Cassius"
                            }
                        }
                    ]
                },
                "User ID": {
                    "number": 1234
                },
                "File CSV": {
                    "files": [
                        {
                            "content": "asd",
                            "name": "templatePlayers.csv",
                            "type": "file"
                        }
                    ],
                    "type": "files"
                }
            }
        }
        
        res = requests.request("POST", readURL, headers=headers, data=json.dumps(NewPageData))
        if(res.status_code == 200):
            response = app.response_class(
                response = json.dumps({
                    'status': res.status_code,
                    'message': 'successful data retrieval',
                    'response': res.json()
                }),
                status=res.status_code,
                mimetype='application/json'
            )
            return response
        else:
            response = app.response_class(
                response = json.dumps({
                    'status': res.status_code,
                    'message': 'Connection failed',
                    'response': res.json()
                }),
                status=res.status_code,
                mimetype='application/json'
            )
            return response 

    @app.route('/v1/notion/gallery', methods=["POST"])
    def Notion_Database():

        data = request.json
        database = data["database-id"]

        payload = {
            "page_size": 100,
            "filter": {
                "and": [
                    {
                        "property": "card-status",
                        "checkbox": {
                            "equals": True
                        }
                    },
                    {
                        "property": "card-title",
                        "rich_text": {
                            "is_not_empty": True
                        }
                    },
                    {
                        "property": "card-subtitle",
                        "rich_text": {
                            "is_not_empty": True
                        }
                    }
                ]
            },
            "sorts": [
                {
                    "property": "Name",
                    "direction": "ascending"
                }
            ]
        }

        if "payload" in data:
            if "page_size" in data["payload"]:
                payload["page_size"] = data["payload"]["page_size"]
            
            if "filter" in data["payload"]:
                if "and" in data["payload"]["filter"]:
                    payload["and"] = payload["and"].extend(data["payload"]["filter"]["and"])

            if "sorts" in data["payload"]:
                payload["sorts"] = payload["sorts"].extend(data["payload"]["sorts"])

        print(payload)

        readURL = f"https://api.notion.com/v1/databases/{database}/query"
        
        res = requests.request("POST",readURL, json=payload, headers=headers)
        
        if(res.status_code == 200):
            results = res.json()["results"]
            data_results = []
            for result in results:
                properties = result["properties"]
                
                buttons = []
                for i in range(1, 4):
                    type = None
                    type_result = properties["typeButton"+str(i)]["select"]
                    type_caption = properties["button"+str(i)+"Caption"]["rich_text"]
                    type_target = properties["button"+str(i)+"Target"]["rich_text"]

                    if type_result != None:
                        type = type_result["name"]

                    caption = None
                    if len(type_caption) > 0:
                        caption = type_caption[0]["plain_text"]
                    
                    target = None
                    if len(type_target) > 0:
                        target = type_target[0]["plain_text"]
                    button = {
                        "url": None,
                        "type": type,
                        "target": target,
                        "actions": [],
                        "caption": caption,
                        "webview_size": None
                    }
                    if caption != None:
                        buttons.append(button)
                value = {
                    "title": properties["card-title"]["formula"]["string"],
                    "buttons": buttons,
                    "subtitle": properties["card-subtitle"]["formula"]["string"],
                    "image_url": properties["card-image"]["formula"]["string"],
                    "action_url": properties["card-url"]["formula"]["string"],
                }
                data_results.append(value)

            response = app.response_class(
                response = json.dumps({
                    'status': res.status_code,
                    'message': 'successful data retrieval',
                    'response': data_results
                }),
                status=res.status_code,
                mimetype='application/json'
            )
            return response
        else:
            response = app.response_class(
                response = json.dumps({
                    'status': res.status_code,
                    'message': 'Connection failed',
                    'response': res.json()
                }),
                status=res.status_code,
                mimetype='application/json'
            )
            return response 
    
    @app.route('/v1/notion/search', methods=["POST"])
    def Notion_Search():
        readURL = "https://api.notion.com/v1/search"

        data = request.json

        payload = data["payload"]

        res = requests.post(readURL, json=payload, headers=headers)
        if(res.status_code in [200, 201]):
            response = app.response_class(
                response = json.dumps({
                    'status': res.status_code,
                    'message': 'successful data retrieval',
                    'response': res.json()
                }),
                status=res.status_code,
                mimetype='application/json'
            )
            return response
        else:
            response = app.response_class(
                response = json.dumps({
                    'status': res.status_code,
                    'message': 'Connection failed',
                    'response': res.json()
                }),
                status=res.status_code,
                mimetype='application/json'
            )
            return response
    
    @app.route('/v1/notion/csv', methods=["POST"])
    def Notion_CSV():

        data = request.json

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Notion-Version": "2022-02-22",
            "Authorization": "Bearer " + data["notion"]["authorization"]
        }
        s = json.dumps(data["data"], separators=(',', ':'))

        json_encoded = base64.b64encode(s.encode('utf-8')).decode('utf-8')

        url = os.getenv('URL')


        csvURL = f"{url}/v1/notion/download/{json_encoded}"
        readURL = f"https://api.notion.com/v1/pages"
        notion = data["notion"]
        database = notion["database_id"]

        NewPageData = {
            "parent": {"database_id": database},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": notion["name"]
                            }
                        }
                    ]
                },
                "User ID": {
                    "type": "number",
                    "number": notion["user_id"]
                },
                "File CSV": {
                    "type": "url",
                    "url": csvURL
                }
            }
        }
        
        res = requests.request("POST", readURL, headers=headers, data=json.dumps(NewPageData))
        if(res.status_code == 200):
            response = app.response_class(
                response = json.dumps({
                    'status': res.status_code,
                    'message': 'successful data retrieval',
                    'response': {
                        'file_csv': csvURL,
                        'notion': res.json()
                    }
                }),
                status=res.status_code,
                mimetype='application/json'
            )
            return response
        else:
            response = app.response_class(
                response = json.dumps({
                    'status': res.status_code,
                    'message': 'Connection failed',
                    'response': res.json()
                }),
                status=res.status_code,
                mimetype='application/json'
            )
            return response 

    @app.route('/v1/notion/download/<path:filename>', methods=['GET','POST'])
    def download(filename):
        json_decoded = base64.b64decode(filename.encode('utf-8')).decode('utf-8')

        df = pd.read_json(json_decoded, orient='records')
        csv = df.to_csv(index = False, sep=';', encoding='utf-8', header=True)

        response_stream = BytesIO(csv.encode())

        return send_file(
            response_stream,
            mimetype="text/csv",
            attachment_filename="export.csv",
            as_attachment=True
        )

    @app.route('/v1/notion/granola/generate-rpe', methods=['POST'])
    def Convert_Json():
        try:
            data = request.json
            def Json(json):
                return [json_.items() for json_ in json]
            _json = []
            for data_ in data["data"]:
                item_ = {
                    'UserID': data_['UserID'],
                    'Cliente': data_['Cliente'],
                    'Box': data_['Box']
                }

                if item_.items() not in Json(_json):
                    _json.append(item_)

            x = {}
            for data_ in data["data"]:
                item_ = {
                    'UserID': data_['UserID'],
                    'Cliente': data_['Cliente'],
                    'Box': data_['Box']
                }
                values_ = {
                    'Producto': data_['Producto'],
                    'Cantidad': data_['Cantidad'],
                    'ItemID': data_['ItemID'],
                    'Packaging': data_['Packaging'],
                }
                for i in range(len(_json)):
                    if item_.items() == _json[i].items():
                        if item_["Cliente"] in x.keys():
                            x[item_["Cliente"]].append(values_)
                        else:
                            x[item_["Cliente"]] = [values_]
                        break
            pack = {
                'ETIQUETA x12': 12,
                'ETIQUETA x6': 6,
                'ETIQUETA': 1
            }

            # define a fuction for key
            def key_func(k):
                return k['Packaging']
            resp = {}
            for i in x.keys():
                items = []
                INFO = sorted(x[i], key=key_func)
                for key, value in groupby(INFO, key_func):
                    restante = []
                    for value_ in list(value):
                        packing = int(pack[value_['Packaging']])
                        cantidad = int(value_['Cantidad'])
                        producto = value_['Producto']
                        if cantidad >= packing:
                            while cantidad >= packing:
                                new_cantidad = cantidad - packing
                                #print(producto + " x"+ str(new_cantidad))
                                items.append(producto + " x"+ str(packing))
                                cantidad = new_cantidad
                            if cantidad > 0:
                                restante.append(producto + " x"+ str(cantidad))
                        else:
                            restante.append(producto + " x"+ str(cantidad))
                    #Analizando los restantes
                    if len(restante)>0:
                        #Primero si a todos puedo meterlos en un paquete
                        total = sum([int(restante_.split(" x")[-1]) for restante_ in restante])
                        if total<=packing:
                            items.append(' + '.join(restante))
                        else:
                            acu = 0
                            rest = []
                            for k in range(len(restante)):
                                acu += int(restante[k].split(" x")[-1])
                                if acu > packing:
                                    new_q = acu - packing
                                    quant = int(restante[k].split(" x")[-1])-new_q
                                    new_i = restante[k].split(" x")[0]+" x"+str(quant)
                                    rest.append(new_i)
                                    items.append(' + '.join(rest))
                                    rest = []
                                    rest.append(restante[k].split(" x")[0]+" x"+str(new_q))
                                else:
                                    rest.append(restante[k])
                            items.append(' + '.join(rest))
                resp[i] = items
            for i in range(len(_json)):
                _json[i]["Packagings"] = len(resp[_json[i]["Cliente"]])
                _json[i]["items"] = resp[_json[i]["Cliente"]]
            response = app.response_class(
                response = json.dumps({
                    'status': 200,
                    'message': 'successful data retrieval',
                    'response': _json
                }),
                status=200,
                mimetype='application/json'
            )
            return response
        except Exception as e:
            response = app.response_class(
                response = json.dumps({
                    'status': 400,
                    'message': 'Connection failed',
                    'response': str(e)
                }),
                status=400,
                mimetype='application/json'
            )
            return response 
    return app
