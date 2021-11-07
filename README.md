# Bitcoin Tesnet Node: Sending Transactions #
Created by Sjors van Heuveln, 1 nov 2021.
The goal is to build a full-fledged operational node.

*Anyone can understand Bitcoin as it's not really changing.
Therefore mentally you can catch up with it.*

### How to Use ###
Run `main.py`.


### OPEN QUESTIONS ###
1. How does the send transaction work.
     * node.send() -> creates Network Envelope [reqs: command & message.serialize()]
     * Tx.serialize() -> Tx_in.serialize + Tx_out.serialize()
2. What is ASM in display sigscript?


### To do ###

1. Handle reject messages. -> when waiting for a message seems to make it process, but that's weird!
2. Check if transactions can get rejected on fees.

<!-- 2. Fix Bloom Filter incoming Txs
     - Parse the transaction manually, see where it goes wrong.
     - I think somehow I'm fishing out the hacks I think, my script mostly works fine.
 -->


### Resources ###
- [Jimmy Song's: Programming Bitcoin PDF](https://www.programming-book.com/python-programming123uo00es0429/)
- [Justmin Moon YouTube](https://www.youtube.com/watch?v=gMmWhiDSius&ab_channel=JustinMoon)
- [Justin Moon GitHub](https://github.com/justinmoon/)
- [Bitcoin Wiki](https://en.bitcoin.it/wiki/Protocol_documentation#tx)


### Tools ###
- Get Testnet coins [here](https://testnet-faucet.mempool.co/).


### Learnings ###
1. Probably: Mempool messages can only be sent to nodes with 1037 services.
      * So 1037/1036 have: NODE_NETWORK_LIMITED, NODE_WITNESS and NODE_BLOOM ACTIVATED
      * 1036 doesn't appear to return merkleblocks. 
          - And it can't as it needs to be a full node!
      
      1 NODE_NETWORK  This node can be asked for full blocks instead of just headers.
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
               -> managed to get this with a less strict bloomfilter, but getting unknown ScriptPubKey Error

3. OP_RETURN: an output trick that is used to store data on the blockchain.
     - Features: 
          * Unspendable (burn coins)
          * Store data (mostly ascii encoded)

     - Rick Astley: https://www.blockchain.com/btc/tx/d29c9c0e8e4d2a9790922af73f0b8d51f0bd4bb19940d9cf910ead8fbe85bc9b
     - Nelson Mandela: https://www.blockchain.com/btc/tx/8881a937a437ff6ce83be3a89d77ea88ee12315f37f7ef0dd3742c30eef92dba
          - Seems like you signal it with 5500 satoshis.
     - Len Sassaman: https://www.blockchain.com/btc/tx/930a2114cdaa86e1fac46d15c74e81c09eee1d4150ff9d48e76cb0697d8e1d72
     - To solve:
          * https://www.blockchain.com/btc-testnet/tx/535d7321491708198a9b776fb1e9765c1795ccb82e2445241e4341e3836cf363
               - Probably part of longer message from this address:https://www.blockchain.com/btc-testnet/address/mxVFsFW5N4mu1HPkxPttorvocvzeZ7KZyk

4. Play sound with: `print('\007')`

5. Taproot = BECH32M (or at least a wrap around)
     - 62 chars
     - OP_1 (81, to send to taproot address) or OP_0 (0, probably to send to for normal bech32) with

6. Reading Blockchain.com
     - It removes varints at e.g. Sigscript
     - It delineates signature and pubkey in the inputs.
     - Provides the necessary material to verify.

7. From Hex to Bytes:
     - The way: bytes.fromhex(hexstring)
     - b'' is not good!

8. Signing transactions:
     - You sign the hash256 of all the transaction data serialized (without the sighash itself)
          * This protects the data for tampering by other nodes.
          * Sighash is signed with privatekey
          * Though the verification process is easy for all nodes.
     - Basically you are proving:
          * You have the public key that generates the address [OP_EQUALVERIFY]
          * Sighash and public key prove you own the privatekey. [OP_CHECKSIG]
          * In short: That you may spend the UTXO.
     - Outputs don't care for a transaction verificaiton
          * You can write the most horrible outputs (I think)
          * As long as the Script reduces to True.
     - Coinbase Transaction:
          * Coinbase + fees are (can be) in 1 output.
          * Blockheight is also somewhere in there I believe.


### Check Later ###
- Stenography: sending messages hidden in images.
