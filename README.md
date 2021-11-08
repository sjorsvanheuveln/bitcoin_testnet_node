# Bitcoin Tesnet Node: Sending Transactions #
Created by Sjors van Heuveln, 1 nov 2021.

![Satoshi City](https://preview.redd.it/98d2sxhnh2t31.jpg?width=3840&format=pjpg&auto=webp&s=7add8087278f2f8847881a2226d3397ac1778d80)

### HOW TO USE ###
Run `main.py`.

<br>

### To do ###

1. Learn on fee calculation
     - Calculate sats per byte per transaction and print to console.
     - What is sats/vbyte?
2. Mainnet:
     - Send the Saylor!
          -> Multiple OP_RETURNS not allowed.
3. UTXO:
     - Make a better UTXO function. So I can see what my address has.
     - Make a class with functions and data.
          - count
          - largest utxo
4. New Tx:
     - Make a BECH32 P2WPKH tx.
          * Spending to is possible already. 
          * Spending from not yet -> witness required.
     - What are all the differences?!!!!
          - What were the reasons to change drom p2pkh?
     - Adjust the address function of the public key to allow multiple adresses.

<!-- 2. Fix Bloom Filter incoming Txs
     - Parse the transaction manually, see where it goes wrong.
     - I think somehow I'm fishing out the hacks I think, my script mostly works fine.
 -->
<br>

### Resources ###
- [Jimmy Song's: Programming Bitcoin PDF](https://www.programming-book.com/python-programming123uo00es0429/)
- [Justmin Moon YouTube](https://www.youtube.com/watch?v=gMmWhiDSius&ab_channel=JustinMoon)
- [Justin Moon GitHub](https://github.com/justinmoon/)
- [Bitcoin Wiki](https://en.bitcoin.it/wiki/Protocol_documentation#tx)
<br>

### Tools ###
- Get Testnet coins:
     * [Mempool.co](https://testnet-faucet.mempool.co/)
     * [CoinfaucetEU](https://coinfaucet.eu/en/btc-testnet)

