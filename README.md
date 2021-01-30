# sporttrade

SQL configuration page:
https://docs.nats.io/nats-streaming-server/configuring/persistence/sql_store

Ref to running dbs:
https://github.com/nats-io/nats-streaming-server/issues/899

Command for nats-streaming-server from go/bin
./nats-streaming-server --port 4223 --store=SQL --sql_driver=mysql --sql_source='nss:password@(127.0.0.1:3306)/nss_db'

This is generally working. I've connected all the pieces. Need to clean up then dockerize and provide write-up. 

TODO: 
1.) ensure requirements are met --- persistent storage timestamps, etc.
  - Check, persistent storage in nss_db in table "Messages" has a timestamp on each message.
  - See other reqs.
1a.) refactor some of the subscription stuff into separate functions
2.) write documentation especially for client service usage
3.) ensure it can run at their speed (1000 messages/sec)
4.) dockerize the entire thing
  - Most important thing
5.) create architecture diagram

---------------------
extra notes:
---------------------

sport trade company
acquired by someone
placing devs now
peer to peer market place for sports betting. combines sports betting with financial hedging.
app is live (Sports Trade): asyncio (starlet)
fastapi

Meeting with Will Sumfest
01/22/2021

4 mobile
15 eng

Requirements:
Spec: 
1. You are given two feeds running locally, sending messages to a local NATS broker. Catalog every message with an associated timestamp into a persistent storage. These messages are serialized via protobuf (), and the spec is outlined in the repository below. 
- Ensure there is a storage volume in the container with a database (prob Postgres). 
- It appears there are separate containers for each feed. 
- protocol buffer - Google open source project - mechanism for serializing structured data: supported in many languages. Faster and smaller than xml. 

- refs:
  - https://blog.conan.io/2019/03/06/Serializing-your-data-with-Protobuf.html
  - Python library for NATS: https://github.com/nats-io/nats.py
 

2. Implement a subscription service that allows users to listen to both feeds in real time. The transport protocol for this service is at your discretion.

- use NATS streaming

3. Ensure exactly once processing semantics for our users and persistent storage.

- This means we need an ack to confirm the receive. 
- Persistent storage needs to persist if container dies
4. You will find the feeds, NATS broker, and protobuf specs here: https://bitbucket.org/will-sumfest/edge-swe-challenge/src/master/
5. Please let us know if you are running on a system other than MacOS or Linux.

-UPDATES:
  - Got files of the events emitting from the sport and event feed (ran docker image and used the terminal to access the fs). 
  - Next is to capture those events (not sure if in NATS image (I assume so, or another separate image?).

- Very similar question: https://stackoverflow.com/questions/57360984/nats-subscriber-continuously-listening-to-publisher 
  - better one: https://stackoverflow.com/questions/63846385/how-do-i-subscribe-to-a-nats-subject-in-python-and-keep-receiving-messages

- compile protocol buffers to be used: https://developers.google.com/protocol-buffers/docs/pythontutorial  

- need to compile the protocol buffers with link above. Then use them to capture the incoming message. I can also run the code locally once I have them for easier testing. 

  - ~/go/bin/nats-server to run nats locally

NEXT:
- it appears that I have captured both of the feeds via my subscribe_feeds.py when everything is running. 
  - What I think I should do next is run the nats-streaming-server because it provides two things:
1.) Persistence. There is a way to store things locally with it. (see email). This also requires NATS streaming according to https://docs.nats.io/developing-with-nats-streaming/streaming)
2.) Publish subscriptions. This will be a separate server to publish things which should allow for high throughput. 
  - The thing is that I need to get the messages there. 

See “When to use NATS Streaming” for basically the description of my project: https://docs.nats.io/developing-with-nats-streaming/streaming 
  - consider this URL as guidance for the streaming service. 
  - it may just be as simple as starting a STAN streamer and publishing on that in the same file? maybe not scalable but easier. Do this first
  - Queues for load balancing: https://docs.nats.io/nats-concepts/queue

 helpful for streaming: https://itnext.io/overview-of-nats-streaming-ea0e80449507
