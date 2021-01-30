import asyncio
from nats.aio.client import Client as NATS
from stan.aio.client import Client as STAN

from gen import event_pb2
from gen import execution_pb2


class StreamService():
    ''' This StreamService class allows a client to easily interact with the STAN
    streaming server on port 4223 in the Docker container. For the POC it runs
    the private _run method upon instantiation. '''

    def __init__(self, event_callback, execution_callback):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(
            self._run(self.loop, event_callback, execution_callback))
        self.loop.run_forever()
        self.loop.close()

    async def _run(self, loop, event_callback, execution_callback):
        print("starting client StreamService...")
        nc = NATS()
        sc = STAN()

        async def disconnected_cb():
            print("Disconnected from StreamService...")

        async def reconnected_cb():
            print("Reconnected to StreamService...")

        await nc.connect("host.docker.internal:4223",
                         reconnected_cb=reconnected_cb,
                         disconnected_cb=disconnected_cb,
                         max_reconnect_attempts=-1,
                         reconnect_time_wait=10,
                         loop=loop)

        # demo client id
        await sc.connect("test-cluster", "client-id-123", nats=nc)

        # example of potential subscription feed names so wildcards could be used in the future
        events_subject = "feed.events"
        executions_subject = "feed.executions"

        # last_received ensures a client won't receive stale messages and starts with
        # most recently published value
        await sc.subscribe(events_subject, start_at="last_received", cb=event_callback)
        await sc.subscribe(executions_subject, start_at="last_received", cb=execution_callback)


def decode_event_message(msg):
    ''' Helper function to decode event messages. '''
    data = event_pb2.event()
    data.ParseFromString(msg.data)
    return data


def decode_execution_message(msg):
    ''' Helper function to decode execution messages. '''
    data = execution_pb2.execution()
    data.ParseFromString(msg.data)
    return data


if __name__ == '__main__':

    async def test_event_callback(msg):
        ''' demo client callback for events '''
        print("client event callback triggered")
        data = decode_event_message(msg)
        # client can operate on data from here
        print("Received:\n", data)

    async def test_execution_callback(msg):
        ''' demo client callback for executions '''
        print("client execution callback triggered")
        data = decode_execution_message(msg)
        # client can operate on data from here
        print("Received:\n", data)

    # instantiate object for demo
    start_stream = StreamService(test_event_callback, test_execution_callback)
