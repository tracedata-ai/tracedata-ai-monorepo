# Task Plan: ExploreSG MK-IV

## Project Overview

AI-powered multi-tenant vehicle rental + tourism platform for Singapore.

## Phases

### Phase 1: Foundation (Weeks 1-2)

- [ ] Project Structure Setup
- [ ] Modular Monolith Foundation
- [ ] Auth Service
- [ ] Fleet Module

### Phase 2: Core Booking (Weeks 3-4)

- [ ] Booking Module
- [ ] Domain Events Implementation
- [ ] Saga Pattern for Reservation

### Phase 3: Customer Agents (Weeks 5-6)

- [ ] Concierge Agent
- [ ] Vehicle Agent
- [ ] Places Agent
- [ ] Support Agent (RAG)

### Phase 4: Telematics & Analytics (Weeks 7-8)

- [ ] Car Simulator
- [ ] Monitoring Agent
- [ ] Analytics Agent

## Architectural Decisions

- **Architecture**: Modular Monolith with Domain Events.
- **AI**: Multi-agent system using LangGraph.
- **Database**: PostgreSQL with Schema-per-module.
