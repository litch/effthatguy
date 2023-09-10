from pyln.testing.fixtures import *
import time

plugin_path = os.path.join(os.path.dirname(__file__), 'effthatguy.py')
pluginopt = {'plugin': plugin_path}
# pluginopt = {}

def test_my_plugin(node_factory, bitcoind):
    print("Testing plugin")

    l1, l2, l3 = node_factory.line_graph(3)
    l1.rpc.plugin_start(plugin_path)
    l1.daemon.wait_for_log("Plugin effthatguy initialized")

    scid_A = l2.rpc.listpeerchannels(l1.info["id"])["channels"][0]["short_channel_id"]

    time.sleep(1)

    l1.fundchannel(l2, 10**6)
    l1.fundchannel(l3, 10**6)
    l1.daemon.wait_for_log("CHANNELD_NORMAL")
    effing = l1.rpc.effthatguy(l2.info['id'])
    assert(effing == [l2.info['id']])

    s = l1.rpc.getinfo()

    eff_another = l1.rpc.effthatguy(scid_A)
    assert(eff_another == [l2.info['id'], scid_A])

    assert(len(l1.getactivechannels()) == 6)

    l2.rpc.disconnect(l1.info["id"], force=True)
    assert(len(l1.getactivechannels()) == 2)

    l1.connect(l2)

    l1.daemon.wait_for_log("Closing channel")

    l2.restart()

    assert(len(l1.getactivechannels()) == 2)
