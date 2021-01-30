import asyncio
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN

from gen import event_pb2
from gen import execution_pb2

EVENT_TOPIC_NAME = "sport_event"
EXECUTION_TOPIC_NAME = "execution"


async def run(loop):
    print("starting message controller...")
    nc = NATS()
    stan_con = NATS()  # nats server connection for streaming
    sc = STAN()

    async def disconnected_cb():
        print("Disconnected...")

    async def reconnected_cb():
        print("Reconnected...")

    await nc.connect("host.docker.internal:4222",
                     reconnected_cb=reconnected_cb,
                     disconnected_cb=disconnected_cb,
                     max_reconnect_attempts=-1,
                     reconnect_time_wait=10,
                     loop=loop)

    await stan_con.connect("host.docker.internal:4223",
                           reconnected_cb=reconnected_cb,
                           disconnected_cb=disconnected_cb,
                           max_reconnect_attempts=-1,
                           reconnect_time_wait=1,
                           loop=loop)
    await sc.connect("test-cluster", "client-1", nats=stan_con)

    async def cb(ack):
        # Log ack to console for POC
        print("Received ack: {}".format(ack.guid))

    async def event_message_handler(msg):
        # parse data from protobuf protocol
        data = event_pb2.event()
        data.ParseFromString(msg.data)
        # Publish the message to the streaming server for clients to consume
        await sc.publish("feed.events", msg.data, ack_handler=cb)

    async def execution_message_handler(msg):
        # parse data from protobuf protocol
        data = execution_pb2.execution()
        data.ParseFromString(msg.data)
        # Publish the message to the streaming server for clients to consume
        await sc.publish("feed.executions", msg.data, ack_handler=cb)

    # Subscribe to both feeds
    await nc.subscribe(EVENT_TOPIC_NAME, "workers", event_message_handler)
    await nc.subscribe(EXECUTION_TOPIC_NAME, "workers", execution_message_handler)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.run_forever()
    loop.close()
