import asyncio
import time
import datetime
import random
import json
import sys
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

from gen import event_pb2
from gen import execution_pb2

EVENT_TOPIC_NAME = "sport_event"
EXECUTION_TOPIC_NAME = "execution"
# to set port on server run: ./nats-server --port 4223


async def run(loop):
    print("starting...")
    nc = NATS()
    stan_con = NATS()
    sc = STAN()

    async def disconnected_cb():
        print("Disconnected...")

    async def reconnected_cb():
        print("Reconnected...")

    await nc.connect("127.0.0.1:4222",
                     reconnected_cb=reconnected_cb,
                     disconnected_cb=disconnected_cb,
                     max_reconnect_attempts=-1,
                     loop=loop)

    await stan_con.connect("127.0.0.1:4223", loop=loop)
    await sc.connect("test-cluster", "client-1", nats=stan_con)

    async def cb(ack):
        print("Received ack: {}".format(ack.guid))

    async def event_message_handler(msg):
        # subject = msg.subject
        # reply = msg.reply

        data = event_pb2.event()
        data.ParseFromString(msg.data)
        # Publish the message to the streaming server for clients to consume
        await sc.publish("feed.events", msg.data, ack_handler=cb)

    async def execution_message_handler(msg):
        # subject = msg.subject  # unnecessary, only here to parse and see message
        # reply = msg.reply
        data = execution_pb2.execution()
        data.ParseFromString(msg.data)
        # Publish the message to the streaming server for clients to consume
        await sc.publish("feed.executions", msg.data, ack_handler=cb)
        # print("Received a message on '{subject} {reply}': {data}".format(
        # subject=subject, reply=reply, data=data))

    # Use queue named 'workers' for distributing requests
    # among subscribers.
    await nc.subscribe(EVENT_TOPIC_NAME, "workers", event_message_handler)
    await nc.subscribe(EXECUTION_TOPIC_NAME, "workers", execution_message_handler)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()
    loop.close()
