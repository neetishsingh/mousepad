from fastapi import FastAPI, Request, Body, WebSocket, WebSocketDisconnect

from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import threading
import datetime
import json
import ssl
import webbrowser

import os
import uvicorn
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import pyautogui
import socket
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware


from fastapi.staticfiles import StaticFiles
app = FastAPI()

connected_clients = set()

current_directory = os.path.dirname(os.path.abspath(__file__))

app.mount("/web", StaticFiles(directory=current_directory +
          "/webbuild/web"), name="static")
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000/*",
    "http://*",
    "*",
    "http://192.168.29.213:8000/*",
    "ws://localhost:8000/",
    "ws://192.168.29.213:8000/*",
    "*//192.168.29.213*",
    "http://0.0.0.0:8000/*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


screenSize = pyautogui.size()

# Queue to store incoming data
data_queue = []
aggregate_period = 0.07  # 1 second


async def process_data():
    while True:
        await asyncio.sleep(aggregate_period)
        if data_queue:
            print(data_queue)
            aggregated_data = {'x': sum(d['x'] for d in data_queue),
                               'y': sum(d['y'] for d in data_queue)}

            moveMouse(aggregated_data['x'], aggregated_data['y'])
            # print('i am doing')
            data_queue.clear()


async def start_processing():
    await process_data()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_processing())
    url = "http://localhost:8000/web/index.html"

    webbrowser.open(url, new=0, autoraise=True)


def moveMouse(x, y):
    scrollfactor = 1.2
    currentMouseX, currentMouseY = pyautogui.position()
    # screenSize[1])
    print(x, y)
    pyautogui.moveTo(currentMouseX+int(x)*scrollfactor,
                     currentMouseY+int(y)*scrollfactor)


def clickMouse():
    pyautogui.click()


@app.get("/")
async def root(request: Request, response_class=HTMLResponse):
    # moveMouse()

    socket.gethostbyname(socket.gethostname())
    ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
          for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

    # {"message": ip+":8000","client_ip":request.client}
    html_content = """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/ipneet")
async def root(request: Request):
    # moveMouse()

    socket.gethostbyname(socket.gethostname())
    ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close())
          for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]

    return {"parent": ip+":8000", "client_ip": request.client}


@app.post("/movemouse/")
def movemouse(data: Dict[Any, Any]):
    data_queue.append(data)
    # print(data)
    # moveMouse(data['x'], data['y'])
    return "h"


@app.post("/mouseaction/")
def mouseAct(data: Dict[Any, Any]):
    print(data)
    if (data["action"] == "tap"):
        pyautogui.click()
    if (data["action"] == "doubletap"):
        pyautogui.click(button='right')
    # print(data)
    # moveMouse(data['x'], data['y'])
    return "h"


@app.post("/keyboardaction/")
def keyboardAct(data: Dict[Any, Any]):
    print(data)
    if (data["action"] == "customtype"):
        pyautogui.write(data["key"], interval=0.05)
    if (data["action"] == "keys"):
        pyautogui.press(data["key"])
    if (data["action"] == "action"):
        if (data["key"] == "VirtualKeyboardKeyAction.Backspace"):
            pyautogui.press("backspace")
        if (data["key"] == "VirtualKeyboardKeyAction.Return"):
            pyautogui.press("enter")

        if (data["key"] == "VirtualKeyboardKeyAction.Space"):
            pyautogui.press("space")
        if (data["key"] == "VirtualKeyboardKeyAction.Shift"):
            pyautogui.press("capslock")

    # print(data)
    # moveMouse(data['x'], data['y'])
    return "h"


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         pyautogui.press('W')
#         print(data[0:len(data)], "<<<<")
#         await websocket.send_text(f"Message text was: {data}")


@app.websocket("/n")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()

            # print(data)
            try:
                data_dict = json.loads(data)
                x = data_dict.get('x')
                y = data_dict.get('y')
                print(x, y)
                if x is not None and y is not None:
                    moveMouse(x, y)  # Call your function to move the mouse
                    # await websocket.send_text("Mouse moved successfully")
                else:
                    print('n')
                   # await websocket.send_text("Invalid data. 'x' and 'y' must be provided.")
            except json.JSONDecodeError:
                print("error")
                # await websocket.send_text("Invalid JSON data")

    except WebSocketDisconnect:
        connected_clients.remove(websocket)


if __name__ == "__main__":
    print("run")
    uvicorn.run(app, host="0.0.0.0",
                port=8000)
