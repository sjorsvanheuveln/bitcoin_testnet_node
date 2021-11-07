# Bitcoin Tesnet Node: Sending Transactions #
Created by Sjors van Heuveln, 1 nov 2021.

![Satoshi City](https://preview.redd.it/98d2sxhnh2t31.jpg?width=3840&format=pjpg&auto=webp&s=7add8087278f2f8847881a2226d3397ac1778d80)

### How to Use ###
Run `main.py`.

<br>
<br>
### OPEN QUESTIONS ###
1. How does the send transaction work.
     * node.send() -> creates Network Envelope [reqs: command & message.serialize()]
     * Tx.serialize() -> Tx_in.serialize + Tx_out.serialize()
2. What is ASM in display sigscript?


### To do ###

1. Learn on fee calculation
     - Calculate sats per byte per transaction and print to console.
     - What is sats/vbyte?

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


