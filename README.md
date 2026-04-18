# Hybrid Trusted Event Pipeline PoC

A proof-of-concept edge platform for trusted handling of heterogeneous communication events, combining MQTT-based ingestion, local storage, and private blockchain anchoring.

## Overview

This project demonstrates how LPWAN-like and LTE-like operational events can be:

- generated from independent communication domains,
- ingested through MQTT,
- stored locally in SQLite,
- hashed for integrity protection,
- anchored into a real private multi-signer Clique PoA blockchain,
- and later verified through blockchain transaction lookup.

The implementation was validated on a Raspberry Pi edge platform using two logically distinct blockchain signer nodes on a single host for reproducibility.

## Key Capabilities

- Hybrid event ingestion from LoRa-like and LTE-like sources
- MQTT-based message convergence
- Local SQLite persistence of raw events
- SHA-256 event hashing
- On-chain anchoring of event hashes
- Private Ethereum-compatible Clique PoA blockchain
- Multi-signer authority setup
- Transaction-level verification through JSON-RPC

## Architecture

```text
LoRa Simulator ----\
                    \
                     > MQTT Broker --> Bridge Service --> SQLite
                    /                                 \
LTE Simulator -----/                                   \
                                                       Private Clique PoA Blockchain
                                                       (2 signers, single host demo)
