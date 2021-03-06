from werkzeug.wrappers import Request, Response
from werkzeug.serving import run_simple
from jsonrpc import JSONRPCResponseManager, dispatcher
from plasma.child_chain.child_chain import ChildChain
from plasma.config import plasma_config
from plasma.root_chain.deployer import Deployer


child_chain = ChildChain(plasma_config['AUTHORITY'], Deployer().get_contract("RootChain/RootChain.sol"))


@Request.application
def application(request):
    # Dispatcher is dictionary {<method_name>: callable}
    dispatcher["submit_block"] = lambda block: child_chain.submit_block(block)
    dispatcher["apply_transaction"] = lambda transaction: child_chain.apply_transaction(transaction)
    dispatcher["get_transaction"] = lambda blknum, txindex: child_chain.get_transaction(blknum, txindex)
    dispatcher["get_current_block"] = lambda: child_chain.get_current_block()
    dispatcher["get_current_block_num"] = lambda: child_chain.get_current_block_num()
    dispatcher["get_block"] = lambda blknum: child_chain.get_block(blknum)
    response = JSONRPCResponseManager.handle(
        request.data, dispatcher)
    return Response(response.json, mimetype='application/json')


if __name__ == '__main__':
    run_simple('localhost', 8546, application)
