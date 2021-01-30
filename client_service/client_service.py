import asyncio
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

from gen import event_pb2
from gen import execution_pb2


class StreamService():

    def __init__(self, event_callback, execution_callback):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(
            self._run(self.loop, event_callback, execution_callback))
        self.loop.run_forever()
        self.loop.close()

    async def _run(self, loop, event_callback, execution_callback):
        print("starting client...")
        nc = NATS()
        sc = STAN()

        async def disconnected_cb():
            print("Disconnected...")

        async def reconnected_cb():
            print("Reconnected...")

        #
        # await nc.connect("127.0.0.1:4223",
        await nc.connect("host.docker.internal:4223",
                         reconnected_cb=reconnected_cb,
                         disconnected_cb=disconnected_cb,
                         max_reconnect_attempts=-1,
                         reconnect_time_wait=1,
                         loop=loop)

        await sc.connect("test-cluster", "client-id-123", nats=nc)

        # Callback called on each message receive
        async def cb(msg):
            print("Received (#{}): {}".format(msg.seq, msg.data))
            print("parsed and saved to db !")
        # Subscribe to get messages since last acknowledged
        events_subject = "feed.events"
        executions_subject = "feed.executions"
        # last_received ensures a client won't receive stale messages and starts with
        # most recently published value
        await sc.subscribe(events_subject, start_at="last_received", cb=event_callback)
        await sc.subscribe(executions_subject, start_at="last_received", cb=execution_callback)


if __name__ == '__main__':

    async def test_event_callback(msg):
        print("client event callback triggered")
        data = event_pb2.event()
        data.ParseFromString(msg.data)
        print("Received:\n", data)  # client can operate on data from here

    async def test_execution_callback(msg):
        print("client execution callback triggered")
        data = execution_pb2.execution()
        data.ParseFromString(msg.data)
        print("Received:\n", data)  # client can operate on data from here

    start_stream = StreamService(test_event_callback, test_execution_callback)


# old stuff
# async def run(loop):
#     print("starting client...")
#     nc = NATS()
#     sc = STAN()

#     async def disconnected_cb():
#         print("Disconnected...")

#     async def reconnected_cb():
#         print("Reconnected...")

#     await nc.connect("127.0.0.1:4223",
#                      reconnected_cb=reconnected_cb,
#                      disconnected_cb=disconnected_cb,
#                      max_reconnect_attempts=-1,
#                      loop=loop)

#     await sc.connect("test-cluster", "listener-3F45", nats=nc)

#     # Callback called on each message receive
#     async def cb(msg):
#         print("Received (#{}): {}".format(msg.seq, msg.data))
#         print("parsed and saved to db !")
#     # Subscribe to get messages since last acknowledged
#     subject = "devices.3F45.events"
#     await sc.subscribe(subject, durable_name="3F45", cb=cb)
#
# if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(run(loop))
    # loop.run_forever()
    # loop.close()
