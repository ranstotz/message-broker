# Takehome Project

## Usage
Run `bash run.sh` to run the project through Docker. Ensure docker-compose is installed.

## Requirements
1.) You are given two feeds running locally, sending messages to a local NATS broker. Catalog every message with an associated timestamp into a persistent storage. These messages are serialized via protobuf, and the spec is outlined in the repository below.
2.) Implement a subscription service that allows users to listen to both feeds in real time. The transport protocol for this service is at your discretion.
3.) Ensure exactly once processing semantics for our users and persistent storage.
4.) You will find the feeds, NATS broker, and protobuf specs here: https://bitbucket.org/will-sumfest/edge-swe-challenge/src/master/
5.) Please let us know if you are running on a system other than MacOS or Linux.

## Description
Below is the overall architecture diagram for the system:
![Alt text](./assets/message-broker.svg)

This system consumes two feeds (event and execution) from the NATS message broker (port 4222) in the `./controller/controller.py` script. The connection to the NATS server is designed to attempt reconections if disconnected, which is a feature of the service. The connection has two subscriptions, one per each feed, and de-serializes the messages to prepare for publication and persistent storage. 

The transport protocol selected to both provide a subscription service and to catalog the messages with a timestamp was NATS Streaming, or STAN. Not only does this protocol provide at-least-once delivery, but also a straightforward configurable persistence mechanism. 

A second connection is created in controller.py to the STAN server (port 4223) which will manage publishing, database storage, and client subscriptions. In the event and execution subscription callbacks, each publish the de-serialized message data to independent subjects (one for events: 'feed.events' and one for executions: 'feed.executions'). Additionally, there is an acknowledgement handler to print the ack id for debug purposes. The published messages are sent to the STAN server which then catalogs the published messages in a MySQL database named `nss_db` in the table `Messages`. The `Messages` table stores `id`, `seq`, `timestamp`, `size`, and `data`. The database also stores other tables out of the box, but these are outside the scope of the project. 

The consumer service is a class called `StreamService` and is located `./client_service/client_service.py`. This class runs as a demo and consumes both feeds from the STAN server. Additionally, it makes reconnect attempts and has two helper functions to allow clients to decode the event and execution methods. Please see comments in code for additional descriptions. 

## Discussion
After developing the architecture and writing most of the code, I discovered that STAN does not guarantee exactly-once-delivery, and can only provide at-least-once-delivery out of the box. First, I changed the client subscription protocol to start at the "last_received" message, which ensures that the live feed begins when their server starts. This ensures no duplication, however if a client is down, it will not receive prior messages (no message vs dup tradeoff). 

So I will provide some thoughts on this. First, we could use the ack IDs inside the messages and compare to prior messages on the client side. Additionally, the messages also have a publication message order which could also be managed on the client side to ensure all messages have been received and they are in the correct order. 

NATS docs recommend using a max ack in flight value to determine how many unacknowledged acks can be sent to a client. Then, an ack wait can be used to decide when the ack for the message has failed and needs to be redelivered. This creates some redelivery scenarios that need thought. 

Links for discussion: https://docs.nats.io/developing-with-nats-streaming/streaming, https://github.com/nats-io/nats-streaming-server/issues/723#issuecomment-452361690 

