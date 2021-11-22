from database import *

def plot_difficulty():
    blocks = get_block(210000, parse_tx_flag = False)
    db = Database('blocks', drop=True)
    db.add_multiple(blocks)
    db.update_block_heights()



    interval = create_interval(0, 300000)
    db.plot('difficulty', interval, 'log')