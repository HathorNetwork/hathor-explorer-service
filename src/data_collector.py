import aiohttp
import asyncio

STATUS_NODES = [
    'node.explorer.hathor.network',
    'node1.mainnet.hathor.network',
    'node2.mainnet.hathor.network'
]

def process_node_status(node_status: dict):
    print(node_status['server']['id'])

async def request_node(session: aiohttp.ClientSession, url: str):
    try:
        async with session.get(url) as resp:
            status = await resp.json()
            process_node_status(status)
    except:
        pass

async def get_nodes_statuses():
    async with aiohttp.ClientSession() as session:
        responses = []
        for node in STATUS_NODES:
            responses.append(asyncio.ensure_future(request_node(session, f"https://{node}/v1a/status")))
            
        await asyncio.gather(*responses)

async def run():
    while True:
        print('Running...')
        asyncio.create_task(get_nodes_statuses())
        await asyncio.sleep(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        asyncio.ensure_future(run())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        print("Closing Loop")
        loop.close()
