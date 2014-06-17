# !/usr/bin/python
from kivy.app import App
from kivy.uix.accordion import Accordion
from kivy.properties import ObjectProperty
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.storage.jsonstore import JsonStore

from lib.isrunning import isrunning
from lib.checklastblock import checklastblock
from lib.bitmonerodloader import bitmonerodloader
from lib.balancecheck import balancecheck
from lib.namecheck import namecheck
from lib.transferfunds import transferfundsrpccall
from lib.simplewalletloader import simplewalletloader
from lib.save_bc import save_bc
from lib.savewallet import storewallet
from lib.cpuminerloader import cpuminerloader

from sys import argv, platform
from os.path import isfile
import argparse
from multiprocessing import Process, Queue


# Signal that will switch to False on shutdown to kill children
kivysignal = True


class SaveBCPopup(Popup):
    def really_save_bc(self):
        self.storebcthread = Process(target=save_bc)
        self.storebcthread.start()
        self.storebcthread.join()
        self.storebcthread.terminate()
        self.storebcthread.join(timeout=3)


class TransferPopup(Popup):
    popup_label = ObjectProperty()

    def __init__(self, amount, address, mixin, paymentid):
        super(TransferPopup, self).__init__()
        self.amount = amount
        self.address = address
        self.mixin = mixin
        self.paymentid = paymentid
        self.popuptext = "Are you sure you want to send {0:0.9f} XMR\n to [size=8]{1}[/size]\n with mixin count {2} and payment id [size=8]{3}[/size]".format(
            float(amount), address, mixin, paymentid)
        self.popup_label.text = self.popuptext

    def transfer(self):
        txid = transferfundsrpccall(self.amount, self.address, self.mixin,  self.paymentid)
        p = TxIDPopup(txid)
        p.open()


class TxIDPopup(Popup):
    txid_label = ObjectProperty()
    def __init__(self, txid):
        super(TxIDPopup, self).__init__()
        self.txid = txid
        self.txid_label.text = "TxID: [ref=txid]{0}[/ref]\n(Click TxID to copy to clipboard)".format(txid)
    def selecttxid(self):
        Clipboard.put(self.txid)


class RootWidget(Accordion):
    """Root Kivy widget class"""
    # Check to see if wallet name and password passed as arguments
    if len(argv) == 1:
        walletname, walletpw = "", ""
    elif len(argv) == 3:
        walletname, walletpw = argv[1], argv[2]
    # Initialize other variables
    address, rawaddress = "uninitialized", "uninitialized"
    balance, unlockedbalance = "uninitialized", "uninitialized"
    blockinfotext = "Last block info stats go here..."
    namecheckmessage = "uninitialized"
    isname = None
    # Setup object properties to be modified/used by Kivy
    # bitmonerod daemon tab
    daemonchecker_label = ObjectProperty()
    daemoninfo_label = ObjectProperty()
    # init simplewallet tab
    namechecker_label = ObjectProperty()
    walletchecker_label = ObjectProperty()
    input_name = ObjectProperty()
    input_pw = ObjectProperty()
    label_myaddress = ObjectProperty()
    label_balance = ObjectProperty()
    label_unlockedbalance = ObjectProperty()
    # transfer tab
    input_address = ObjectProperty()
    input_amount = ObjectProperty()
    input_mixin = ObjectProperty()
    input_paymentid = ObjectProperty()
    # mining tab
    minerurl_input = ObjectProperty()
    mineruser_input = ObjectProperty()
    minerpw_input = ObjectProperty()
    minerthreads_input = ObjectProperty()

    # Setup queues, signals, and workers
    isrunningjobqueue, isrunningresultsqueue = Queue(), Queue()
    checklastblockjobqueue, checklastblockresultsqueue = Queue(), Queue()
    loadwalletresultsqueue = Queue()
    checkbalancejobqueue, checkbalanceresultsqueue = Queue(), Queue()
    checknamejobqueue, checknameresultsqueue = Queue(), Queue()
    daemonrunning = None
    walletrunning = None
    minerrunning = None
    workers = [
        Process(target=isrunning,
                args=(isrunningjobqueue, isrunningresultsqueue)),
        Process(target=checklastblock,
                args=(checklastblockjobqueue, checklastblockresultsqueue)),
        Process(target=balancecheck,
                args=(checkbalancejobqueue, checkbalanceresultsqueue)),
        Process(target=namecheck,
                args=(checknamejobqueue, checknameresultsqueue))
    ]

    def __init__(self, **kwargs):
        super(RootWidget, self).__init__(**kwargs)
        self.workers[0].start()
        self.workers[1].start()
        self.workers[2].start()
        self.workers[3].start()
        Clock.schedule_interval(self.checkisrunning, 0.1)
        Clock.schedule_interval(self.getblockinfo, 1)
        Clock.schedule_interval(self.checkbalance, 1)
        Clock.schedule_interval(self.checkname, 0.1)
        # load data if it exists
        if isfile('forms.json'):
            try:
                store = JsonStore('forms.json')
                self.input_name.text = store.get('forms')['walletname']
                self.input_address.text = store.get('forms')['sendtoaddress']
                self.input_amount.text = store.get('forms')['amount']
                self.input_mixin.text = store.get('forms')['mixin']
                self.input_paymentid.text = store.get('forms')['paymentid']
                self.minerurl_input.text = store.get('forms')['mineraddress']
                self.mineruser_input.text = store.get('forms')['mineruser']
                self.minerpw_input.text = store.get('forms')['minerpw']
                self.minerthreads_input.text = store.get('forms')[
                    'minerthreads']
            except:
                pass

    def checkisrunning(self, dt):
        """Check if daemon is running"""
        try:
            self.daemonrunning, daemoncheckerlabeltext, self.walletrunning, walletcheckerlabeltext, self.minerrunning = self.isrunningresultsqueue.get_nowait()
            self.daemonchecker_label.text = daemoncheckerlabeltext
            self.walletchecker_label.text = walletcheckerlabeltext
        except:
            pass
        self.isrunningjobqueue.put(kivysignal)

    def getblockinfo(self, dt):
        """Try to update daemon stats"""
        try:
            self.blockinfotext = self.checklastblockresultsqueue.get_nowait()
        except:
            pass
            # blockinfotext = "Last block info:\n No RPC info available."
        self.daemoninfo_label.text = self.blockinfotext
        self.checklastblockjobqueue.put((self.daemonrunning, kivysignal))

    def launchdaemon(self):
        """launch the bitmonerod daemon in rpc mode"""
        if not self.daemonrunning:
            self.launchdaemonthread = Process(target=bitmonerodloader)
            self.launchdaemonthread.start()
            self.daemonrunning = True

    def save_bc(self):
        p = SaveBCPopup()
        p.open()

    def checkbalance(self, dt):
        """Try to update balance stats"""
        try:
            self.balance, self.unlockedbalance, self.rawaddress = self.checkbalanceresultsqueue.get_nowait()
            self.label_balance.text = self.balance
            self.label_unlockedbalance.text = self.unlockedbalance
            self.address = '[color=00ffff][ref=addressselection]' + self.rawaddress + '[/ref][/color]'
            self.label_myaddress.text = self.address
        except:
            pass
        try:
            wallet, self.address, self.rawaddress = self.loadwalletresultsqueue.get_nowait()
            self.label_myaddress.text = self.address
        except:
            pass
        self.checkbalancejobqueue.put((self.walletrunning, kivysignal))

    def launchwallet(self):
        """create wallet if necessary and then launch in rpc mode"""
        if not self.walletrunning:
            self.walletname = self.input_name.text
            self.walletpw = self.input_pw.text
            self.launchwalletthread = Process(target=simplewalletloader,
                                              args=(self.walletname,
                                                    self.walletpw,
                                                    self.isname))
            self.launchwalletthread.start()
            self.walletrunning = True
            self.storeformdata()

    def checkname(self, dt):
        """Check if wallet name exists in local directory"""
        self.walletname = str(self.input_name.text)
        self.checknamejobqueue.put((self.walletname, kivysignal))
        if not self.walletname:
            self.walletname = "No filename"
            # print "no file!"
        try:
            self.isname, self.namecheckmessage = self.checknameresultsqueue.get_nowait()
            # print self.isname
        except:
            pass
        if self.walletrunning:
            self.namecheckmessage = ""
        self.namechecker_label.text = self.namecheckmessage

    def selectaddress(self):
        """copy address to clipboard when user clicks"""
        print('User clicked on ', self.rawaddress)
        # Clipboard.put(self.rawaddress)
        self.input_address.copy(self.rawaddress)

    def savewallet(self):
        self.storewalletthread = Process(target=storewallet)
        self.storewalletthread.start()
        self.storewalletthread.join(timeout=3)
        self.storewalletthread.terminate()
        self.storewalletthread.join()

    def transferfunds(self):
        """initiate transfer of funds to new address"""

        p = TransferPopup(self.input_amount.text, self.input_address.text,
                          self.input_mixin.text, self.input_paymentid.text)
        p.open()

    def transfer(self):
        self.transferthread = Process(target=transferfundsrpccall,
                                      args=(self.amount.text, self.address.text,
                                            self.mixin.text,
                                            self.paymentid.text))
        self.transferthread.start()
        self.transferthread.join()
        self.transferthread.terminate()
        self.transferthread.join(timeout=3)

    def launchminer(self):
        try:
            if not self.minerrunning:
                self.launchminerthread = Process(target=cpuminerloader,
                                                 args=(self.minerurl_input.text,
                                                       self.mineruser_input.text,
                                                       self.minerpw_input.text,
                                                       self.minerthreads_input.text))
                self.launchminerthread.start()
                self.minerrunning = True
                self.storeformdata()
        except:
            pass

    def storeformdata(self):
        store = JsonStore('forms.json')
        store.put('forms',
                  walletname=self.input_name.text,
                  sendtoaddress=self.input_address.text,
                  amount=self.input_amount.text,
                  mixin=self.input_mixin.text,
                  paymentid=self.input_paymentid.text,
                  mineraddress=self.minerurl_input.text,
                  mineruser=self.mineruser_input.text,
                  minerpw=self.minerpw_input.text,
                  minerthreads=self.minerthreads_input.text)


class KivyWalletApp(App):
    def build(self):
        return RootWidget()


if __name__ == '__main__':
    KivyWalletApp().run()
    kivysignal = False
    for i in RootWidget.workers:
        print i.name
        i.terminate()
        i.join()

