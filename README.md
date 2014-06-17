# Cryptonote RPC wallet GUI
This is a GUI frontend that runs on top of bitmonerod, simplewallet (in RPC mode), and optionally LucasJones or Wolf's cryptonight cpuminer. **This program is an alpha version, and although I don't think there is really any way to screw up your wallet, please exercise some modicum of caution (i.e. backup your wallet key file(s)).**

## Installation
### Windows, Linux, and Mac
The requirements for running the program are: Python 2.7 (or 2.6 may work), Kivy 1.8 (at least 1.4), and pygame 1.9.1 (others may work). If you have these requirements, then you just need to either add your binaries (bitmonerod(.exe), simplewallet(.exe), and optionally minerd(.exe)) and optionally wallet files to your cryptonoteRPCwalletGUI folder, or unzip the cryptonoteRPCwalletGUI contents into the folder where you currently have your binaries and wallet files. For the time being, they have to be in the same local directory.

Currently there are no binaries available. I'm in the process of trying to compile an exe for Windows, and subsequently I will try to create binaries for linux and possibly Mac. I've tested the program on Windows 7 & 8.1 and Debian Wheezy, and it seems to work OK. I think it should also work on Mac, but I haven't been able to test that yet.

## Running
It should be OK to launch the program with an instance of bitmonerod, simplewallet, or minerd running, but the program won't allow you to launch another instance of these programs if it detects they are already running. So, unless you know that you are running bitmonerod and simplewallet in RPC mode on default ports, it's probably best to just launch them from within the GUI program. If you close just the GUI though, it should be fine to relaunch when one or all of the binaries are already running.

You can pass your wallet filename and password as arguments on the commandline, if you're launching from the command line, however this is currently not done in the most robust way possible, so make sure you just pass two arguments, the first being wallet name and second password, or the program will probably fail to start. I'm looking to make this more robust using argparse rather than argv.

One known issue is that a wallet created on Windows won't/may not work directly on a Linux machine. A workaround is to delete the wallet bin file, but keep the keys file; simplewallet will rebuild the bin file on Linux and the wallet should work.

## Future Work
There are several features I'd like to implement, the most important of which is probably a table or file keeping a record of all incoming and outgoing transactions. This is a really key feature that should probably be a part of any wallet, but I'm still having some trouble with incoming transactions, so it is delayed for the time being. 

Another thing I want to change is using argparse rather than argv to parse command line arguments. This should make the program more robust (less crashy) and offer the user additional help at the command line. I probably want to clean up the interface and prettify it a bit more too. I'm open to suggestions too, so please open an issue or email me if you have any ideas, complaints, etc.
