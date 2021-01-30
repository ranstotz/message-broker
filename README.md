# message-broker

SQL configuration page:
https://docs.nats.io/nats-streaming-server/configuring/persistence/sql_store

Ref to running dbs:
https://github.com/nats-io/nats-streaming-server/issues/899

Command for nats-streaming-server from go/bin
./nats-streaming-server --port 4223 --store=SQL --sql_driver=mysql --sql_source='nss:password@(127.0.0.1:3306)/nss_db'

This is generally working. I've connected all the pieces. Need to clean up then dockerize and provide write-up. 

TODO: 
1.) Requirements are met. Describe each with documentation in the README.
2.) Create architecture diagram
3.) Email Will with Repo (maybe change name?) and describe project/provide exctitement about using the new tech. 

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

2. Implement a subscription service that allows users to listen to both feeds in real time. The transport protocol for this service is at your discretion.

3. Ensure exactly once processing semantics for our users and persistent storage.

4. You will find the feeds, NATS broker, and protobuf specs here: https://bitbucket.org/will-sumfest/edge-swe-challenge/src/master/
5. Please let us know if you are running on a system other than MacOS or Linux.
