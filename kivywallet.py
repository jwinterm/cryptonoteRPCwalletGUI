from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.core.clipboard import Clipboard

from functions.bitmonerodloader import bitmonerodloader
from functions.checkbalance import checkbalancerpccall
from functions.transferfunds import transferfundsrpccall
from functions.simplewalletloader import simplewalletloader

from sys import argv
from multiprocessing import Process, Queue

class RootWidget(GridLayout):
    """Root Kivy widget class"""
    #Ininitalize variables
    if len(argv) == 1:
        walletname, walletpw = "", ""
    elif len(argv) == 3:
        walletname, walletpw = argv[1], argv[2]
    address, rawaddress = "uninitialized", "uninitialized"
    balance, unlockedbalance = "uninitialized", "uninitialized"

    #Setup object properties to be modified/used
    input_name = ObjectProperty()
    input_pw = ObjectProperty()
    label_myaddress = ObjectProperty()
    label_balance = ObjectProperty()
    label_unlockedbalance = ObjectProperty()
    input_address = ObjectProperty()
    input_amount = ObjectProperty()
    input_mixin = ObjectProperty()

    walletqueue = Queue()

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)

    def launchdaemon(self):
        """launch the bitmonerod daemon in rpc mode"""
        bitmonerodloader()

    def launchwallet(self):
        """create wallet if necessary and then launch in rpc mode"""
        walletthread = Process(target=simplewalletloader, args=(self.input_name.text, self.input_pw.text, self.walletqueue))
        walletthread.start()
        walletthread.join()
        self.walletname, self.address, self.rawaddress = self.walletqueue.get()
        self.input_name.text = self.walletname
        self.input_name.background_color = (0.1,0.8,0.8,1)
        self.label_myaddress.text = self.address

    def checkbalance(self):
        """get balance info from rpc"""
        self.balance, self.unlockedbalance = checkbalancerpccall()
        self.label_balance.text = self.balance
        self.label_unlockedbalance.text = self.unlockedbalance

    def selectaddress(self):
        """copy address to clipboard when user clicks"""
        print('User clicked on ', self.rawaddress)
        Clipboard.put(self.rawaddress)

    def transferfunds(self):
        """initiate transfer of funds to new address"""
        transferfundsrpccall(self.input_amount.text, self.input_address.text, self.input_mixin.text)
        self.checkbalance()


class KivyWalletApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    KivyWalletApp().run()