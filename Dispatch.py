import urllib.request
import json

class Dispatch:
    def __init__(self):
        self.dispatchID = 0
    def setDispatchID(self, aDispatchID):
        self.dispatchID = aDispatchID