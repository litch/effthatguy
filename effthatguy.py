#!/usr/bin/env python3
from pyln.client import Plugin
import pickle

plugin = Plugin()
datastore_key = ['effthatguy', 'descriptors']

@plugin.method("effthatguy")
def effthatguy(plugin, descriptor="", **kwargs):
    """
    Register a peer_id  to end your relationship with next
    time they connect.
    """
    if descriptor == "":
        return plugin.descriptors

    # put the descriptor in the store
    plugin.log("Received descriptor {}".format(descriptor))
    descriptors = plugin.descriptors
    descriptors.append(descriptor)
    plugin.descriptors = descriptors
    plugin.log("Descriptors are now {}".format(descriptors))
    persist_descriptors(plugin)

    return descriptors

@plugin.method("effthatguy-clear")
def effthatguy_clear(plugin, **kwargs):
    """
    Clear the list of peer ids scheduled for closure
    """
    plugin.log("Clearing descriptors")
    plugin.descriptors = []
    persist_descriptors(plugin)
    return plugin.descriptors

def persist_descriptors(plugin):
    hexstr = pickle.dumps(plugin.descriptors).hex()
    plugin.rpc.datastore(key=datastore_key, hex=hexstr, mode="create-or-replace")

def new_datastore():
    return []

def load_from_datastore(plugin):
    entries = plugin.rpc.listdatastore(key=datastore_key)['datastore']
    if len(entries) == 0:
        plugin.log(f"Creating a new datastore '{datastore_key}'", 'debug')
        return new_datastore()
    persist = pickle.loads(bytearray.fromhex(entries[0]["hex"]))

    plugin.log(f"Reopened datastore '{datastore_key}' with {persist} ", 'debug')
    return persist


@plugin.init()
def init(options, configuration, plugin):
    # Fetch the list of descriptors from the store
    # and register them with the plugin

    preloaded_descriptors = load_from_datastore(plugin)

    if preloaded_descriptors:
        plugin.log("Preloaded descriptors {}".format(preloaded_descriptors))
        plugin.descriptors = preloaded_descriptors
    else:
        plugin.log("No preloaded descriptors")
        plugin.descriptors = []

    plugin.log("Plugin effthatguy initialized")

@plugin.subscribe("connect")
def on_connect(plugin: Plugin, **kwargs):
    # {
    #   "connect": {
    #     "id": "02f6725f9c1c40333b67faea92fd211c183050f28df32cac3f9d69685fe9665432",
    #     "direction": "in",
    #     "address": "1.2.3.4:1234"
    #   }
    # }
    connect = kwargs["connect"]
    plugin.log("Received connect {}".format(connect))
    descriptors = plugin.descriptors

    matcher = connect.get("id")

    for descriptor in descriptors:
        if descriptor == matcher:
            plugin.log("Identified peer has connected, closing")
            channels = plugin.rpc.listpeerchannels(connect.get("id")).get("channels", [])
            for channel in channels:
                plugin.log("Closing channel {}".format(channel.get("channel_id")))
                close_channel(channel.get("channel_id"))
        else:
            plugin.log("Peer {} not in descriptors".format(connect.get("id")))


def close_channel(channel_id):
    plugin.log("Closing channel {}".format(channel_id))
    plugin.rpc.close(channel_id)


plugin.run()

