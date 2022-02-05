# coap_client.py
import asyncio
import json

from aiocoap import Message, Context, POST


SERVER_IP = '192.168.43.92'
SERVER_PORT = 5000


async def main():
    context = await Context.create_client_context()
    request_data = {'image': 0}
    payload = json.dumps(request_data).encode('utf-8')

    request = Message(
                code=POST,
                payload=payload,
                uri=f'coap://{SERVER_IP}:{SERVER_PORT}/recognize')

    response = await context.request(request).response
    response_data = json.loads(request.payload)
    print(f'Result: {response.code}\n{response_data}')


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
