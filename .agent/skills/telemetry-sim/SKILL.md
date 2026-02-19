# Telemetry Simulation Skill

## Description

This skill enables the simulation of real-time vehicle telemetry data (GPS, tire pressure, fuel, speed) and publishes it via MQTT to RabbitMQ for the Monitoring Agent to consume.

## Instructions

1. Ensure RabbitMQ with MQTT plugin is running.
2. Configure the simulation parameters in `scripts/config.json`.
3. Run the telemetry loop using `python scripts/telemetry_loop.py`.

## Constraints

- Do not exceed 100 messages per second per vehicle.
- Use UUIDs for vehicle identification.
- Data must be randomized within realistic ranges.
