# Bitcoin Tesnet Node: Sending Transactions #
Created by Sjors van Heuveln, 1 nov 2021.
The goal is to build a full-fledged operational node.

Current Features:
1. Send Tx
2. Get Mempool
3. Get Blocks
<br/>

### Receiving Testnet Coins ###
Send yourself some testnet coins [here](https://testnet-faucet.mempool.co/).
<br/>

### How to Use ###
Run `main.py`.
<br/>

### Resources ###
- [Jimmy Song's: Programming Bitcoin PDF](https://www.programming-book.com/python-programming123uo00es0429/)
- [Justmin Moon YouTube](https://www.youtube.com/watch?v=gMmWhiDSius&ab_channel=JustinMoon)
- [Justin Moon GitHub](https://github.com/justinmoon/)
- [Bitcoin Wiki](https://en.bitcoin.it/wiki/Protocol_documentation#tx)
<br/>

### Learnings ###
1. Probably: Mempool messages can only be sent to nodes with 1037 services.
      * So 1037/1036 have: NODE_NETWORK_LIMITED, NODE_WITNESS and NODE_BLOOM ACTIVATED
      * 1036 doesn't appear to return merkleblocks. 
          - And it can't as it needs to be a full node!
      
      1  NODE_NETWORK  This node can be asked for full blocks instead of just headers.
      2 NODE_GETUTXO  See BIP 0064
      4 NODE_BLOOM  See BIP 0111
      8 NODE_WITNESS  See BIP 0144
      16  NODE_XTHIN  Never formally proposed (as a BIP), and discontinued. Was historically sporadically seen on the network.
      64  NODE_COMPACT_FILTERS  See BIP 0157
      1024  NODE_NETWORK_LIMITED  See BIP 0159

2. FILTERED_BLOCKS return the amount of merkletrees back between your start block and the first block than contains your address.
     - So basically I still don't know what is the significance of the bloomfilter.
          * As I still get one transaction and the whole tree.
          * I can imagine this works when you don't have the blockchain and want verification.
          * I think I should receive more transactions.

<br/>

### To do ###
1. Get UTXOs of my pubkey.
2. Rewrite the scripting for me to learn.
3. Create a fake pubscript that locks a message on the testnet blockchain.
4. Automate sending
5. Check other networking commands.
6. Create a function to find nodes with 1036/1037 services.

<br/>

### Completed Tasks ###
- Send a transaction with Jimmy's libraries.
- Outputting txID when sending.
<br/>

### Check Later ###
- Stenography: sending messages hidden in images.
<br/>