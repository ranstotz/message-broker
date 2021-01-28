import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

from gen import event_pb2
from gen import execution_pb2

EVENT_TOPIC_NAME = "sport_event"
EXECUTION_TOPIC_NAME = "execution"


async def run(loop):
    nc = NATS()

    async def disconnected_cb():
        print("Disconnected...")

    async def reconnected_cb():
        print("Reconnected...")

    await nc.connect("127.0.0.1:4222",
                     reconnected_cb=reconnected_cb,
                     disconnected_cb=disconnected_cb,
                     max_reconnect_attempts=-1,
                     loop=loop)

    async def event_message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = event_pb2.event()
        data.ParseFromString(msg.data)
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    async def execution_message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = execution_pb2.execution()
        data.ParseFromString(msg.data)
        print("Received a message on '{subject} {reply}': {data}".format(
            subject=subject, reply=reply, data=data))

    # Use queue named 'workers' for distributing requests
    # among subscribers.
    await nc.subscribe(EVENT_TOPIC_NAME, "workers", event_message_handler)
    await nc.subscribe(EXECUTION_TOPIC_NAME, "workers", execution_message_handler)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()
    loop.close()
