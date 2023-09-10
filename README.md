Sometimes you have a channel with a peer and you really don't want to have that channel with them anymore - maybe because they are flaky about connectivity or whatever, and they are offline when you decide you want to be done with them.  You don't *totally* hate the situation, so you don't want to force close the channel, but you just want to close the channel next time they come online.  This plugin is for you.

# Usage

You provide the peer_id (pubkey) for that peer, and next time they connect to you, the channel will be closed.

        $ lightning-cli effthatguy <peer_id>
        [peer_id]


If you change your mind, you can clear the list.

        $ lightning-cli effthatguy-clear

If you had a very long list, and want to remove a single entry,
then presumably you had made some poor life choices, and will need
to rebuild the list.  PR's welcome to add that feature though ;)