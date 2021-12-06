#!/bin/python3

import os
import signal
from time import sleep

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

APPINDICATOR_ID = 'cardano-net-select'
CURRPATH = os.path.dirname(os.path.realpath(__file__))


def main():
    check_node_status()

    cardano_icon = CURRPATH + '/cardano_status_icon.svg'
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, cardano_icon ,
                                           appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    gtk.main()


def build_menu():
    menu = gtk.Menu()

    item_mainnet = gtk.RadioMenuItem(label = 'Mainnet')
    item_mainnet.connect('activate', activate_item)

    item_testnet = gtk.RadioMenuItem(label = 'Testnet', group=item_mainnet)
    item_testnet.connect('activate', activate_item)

    item_disabled = gtk.RadioMenuItem(label = 'Disabled', group=item_mainnet)
    item_disabled.connect('activate', activate_item)

    seperator = gtk.SeparatorMenuItem()

    item_quit = gtk.MenuItem(label='Quit')
    item_quit.connect('activate', quit)

    menu.append(item_mainnet)
    menu.append(item_testnet)
    menu.append(item_disabled)
    menu.append(seperator)
    menu.append(item_quit)

    status = check_wallet_status()

    if status == 'Disabled':
        item_disabled.set_active(True)
    elif status == 'Mainnet':
        item_mainnet.set_active(True)
    elif status == 'Testnet':
        item_testnet.set_active(True)

    menu.show_all()
    return menu


def activate_item(source):
    button_state = source.get_label()
    print('Button state: ' + button_state)

    current_system_state = check_wallet_status()
    print('System state: ' + current_system_state)

    if current_system_state != button_state:
        print('Not equal')

        # current is disabled
        if current_system_state == 'Disabled':
            print('current state disabled')
            new_state = button_state.lower()
            control_status_wallet_backend(new_state, 'start')

        elif current_system_state == 'Mainnet':
            print('current state Main')
            control_status_wallet_backend('mainnet', 'stop')

            if button_state == 'Testnet':
                control_status_wallet_backend('testnet', 'start')

        elif current_system_state == 'Testnet':
            print('current state Test')
            control_status_wallet_backend('testnet', 'stop')

            if button_state == 'Mainnet':
                control_status_wallet_backend('mainnet', 'start')
    else:
        print('State is good')


def check_node_status():
    status_mainnet = os.system('systemctl is-active --quiet cardano-mainnet.service')
    status_testnet = os.system('systemctl is-active --quiet cardano-testnet.service')

    # Are the nodes running?
    if status_mainnet == 0:
        mainnet_active = True
        #print('Mainnet is active:' + str(mainnet_active))
    else:
        mainnet_active = False

    if status_testnet == 0:
        testnet_active = True
        #print('Testnet is active:' + str(testnet_active))
    else:
        testnet_active = False

    if testnet_active is False or mainnet_active is False:
        print('There is a problem with the node')
        quit()


def check_wallet_status():

    status_mainnet_wallet = os.system('systemctl is-active --quiet cardano-mainnet-wallet.service')
    status_testnet_wallet = os.system('systemctl is-active --quiet cardano-testnet-wallet.service')

    if status_mainnet_wallet == 0:
        mainnet_wallet_active = True
    else:
        mainnet_wallet_active = False
    print('Mainnet wallet active: ' + str(mainnet_wallet_active))

    if status_testnet_wallet == 0:
        testnet_wallet_active = True
    else:
        testnet_wallet_active = False
    print('Testnet wallet active: ' + str(testnet_wallet_active))

    status = 'Disabled'

    if mainnet_wallet_active:
        status = 'Mainnet'

    if testnet_wallet_active:
        status = 'Testnet'

    #print(status)
    return status


def control_status_wallet_backend(net_type, to_status):

    execute = os.system('systemctl ' + to_status + ' cardano-' + net_type + '-wallet.service')
    sleep(3)
    status = os.system('systemctl is-active --quiet cardano-' + net_type + '-wallet.service')
    return status


def quit(source):
    gtk.main_quit()


if __name__ == "__main__":
    main()
