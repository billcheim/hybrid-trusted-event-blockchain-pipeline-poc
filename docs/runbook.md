# Runbook

This document describes the execution order for the Hybrid Trusted Event Pipeline PoC.

## Terminal layout

- **T1**: helper commands / optional LTE simulator
- **T2**: blockchain node 1
- **T3**: blockchain node 2
- **T4**: bridge service
- **T5**: LoRa simulator
- **T6**: checks / curl / SQLite

## 1. Start blockchain node 1

```bash
cd ~/hybrid-demo-export
docker run --rm -it \
--network host \
-v /home/bill/hybrid-demo/geth-node1-data:/root/.ethereum \
-v /home/bill/hybrid-demo/geth-password.txt:/root/geth-password.txt \
ethereum/client-go:alltools-v1.13.14 \
geth \
  --datadir /root/.ethereum \
  --networkid 424242 \
  --http \
  --http.addr 127.0.0.1 \
  --http.port 8545 \
  --http.api eth,net,web3,personal,miner,admin,clique \
  --authrpc.addr 127.0.0.1 \
  --authrpc.port 8551 \
  --port 30303 \
  --nodiscover \
  --nat extip:127.0.0.1 \
  --allow-insecure-unlock \
  --unlock 0xE3f908D24e07a569Abf2deF2d85a1D6d4C2448Be \
  --password /root/geth-password.txt \
  --mine \
  --miner.etherbase 0xE3f908D24e07a569Abf2deF2d85a1D6d4C2448Be
