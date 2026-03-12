# Project Details

## **1. Program Objectives and Outcomes**

The primary goal of this graduate certificate is for participants to learn how to design, architect, and deploy AI systems that are responsible, ethical, explainable, and secure. Key themes include:

- **Explainable and Responsible AI:** Designing accountable, transparent, and fair systems.
- **AI Cybersecurity:** Identifying vulnerabilities and formulating security strategies for AI-powered defenses and attacks.
- **Agentic AI Architecture:** Leading the design of autonomous, multi-agent systems.
- **Integration and Deployment:** Utilizing MLSecOps and LLMSecOps to streamline the entire machine learning and large language model lifecycle.

### **2. Practice Module Overview**

The Practice Module is the culmination of the four course modules, where participants demonstrate their mastery through a group project (100% of the grade); there is no written exam.

- **Prerequisites:** Participants must have successfully completed or been exempted from the four required course modules.
- **Team Composition:** Groups are comprised of 4 to 5 members.
- **Effort Estimate:** Each participant is expected to contribute approximately 15 days of effort over several weeks.

### **3. Project Requirements and Deliverables**

Participants must source a suitable project from their own organizations or ideas that adequately demonstrates skills from all four modules.

#### **A. Key Project Deliverables**

- **Project Proposal:** Must include the title, sponsor (if applicable), members, business problem context, scope of work (addressing trust, fairness, security, etc.), and effort estimates.
- **Group Project Report:** A comprehensive document covering system architecture, agent design, explainable AI practices, an AI security risk register, and the MLSecOps pipeline.
- **Individual Project Report:** Details a participant's specific contribution, focusing on the design, implementation, and testing of a specific agent.
- **Project Presentation:** A formal presentation including a system demo.

#### **B. Assessment Components**

The assessment is divided equally between team-based and individual contributions:

| Assessment Component       | Weight (Company Sponsored) | Weight (Not Sponsored) |
| :------------------------- | :------------------------- | :--------------------- |
| **Team Based**             | **50%**                    | **50%**                |
| Project Presentation       | 20%                        | 20%                    |
| Project Report             | 30%                        | 30%                    |
| **Individual Based**       | **50%**                    | **50%**                |
| Design of one agent        | 10%                        | 13%                    |
| Implementation/Testing     | 10%                        | 13%                    |
| Individual Reflection      | 10%                        | 14%                    |
| Peer Assessment            | 10%                        | 10%                    |
| Company Sponsor Assessment | 10%                        | N/A                    |

### **4. Important Schedule and Deadlines**

The project spans from early March to mid-May:

- **Proposal Submission:** 5–10 March 2026.
- **Project Conduct & Fortnightly Progress Reports:** 14 March – 23 April 2026.
- **Project Presentation:** 24 April – first week of May 2026.
- **Final Report Submission:** One week after the presentation.
- **Peer Assessment:** Early to mid-May 2026.

### **5. Graduation Requirements**

- **Minimum Pass:** A minimum score of 20% (Grade D) in individual assessment.
- **Certificate Award:** Minimum overall score of 50% (Grade C).
- **MTech Eligibility:** A minimum grade point average of 60% (Grade B-) is required to be eligible for Master of Technology enrollment.

### **6. Questions to Consider**

The "Questions to Consider" for the project are as follows:

- What are the key pain points in current workflows that multi-agent systems can address?
- What additional value-creation opportunities arise specifically from introducing a multi-agent AI system, even beyond addressing today's workflow gaps? (Example: In a telemedicine platform, could autonomous agents proactively identify hidden risks, such as medication interactions?)
- Justify the pros and cons for such agentic AI system adoption or implementation?
- Who are the key stakeholders of this project?
- How should the agents coordinate to ensure a seamless user experience?
- What are the expected benefits of using a modular, agentic AI architecture versus a monolithic chatbot or simple rules-based automation? (e.g., reduced workload, better patient guidance, flexibility, explainability, traceability)
- How can these benefits be demonstrated during the project demo or presentation? (e.g., scenarios where agents show autonomy, handle queries responsibly, escalate appropriately)
- What scale (e.g., concurrent patient sessions) is the solution designed to support?
- How can this scalability claim be demonstrated or justified? (e.g., load tests, architectural scalability characteristics)
- How does the solution ensure explainability and traceability of agent decisions?
- What safeguards are in place to mitigate bias, ensure fairness, accountability, trust and assurance during deployment?
- What common services (e.g., shared memory, logs) will be required to support these agents?
- What reusable libraries or frameworks (e.g., LangChain, LangGraph) are leveraged for agent orchestration?
- What are the AI-specific security risks (e.g., prompt injection, hallucinations, adversarial prompts) and how are they mitigated?
- How does the design ensure safe behaviour even under malicious or unexpected inputs?
- Which part of the AI system lifecycle can be automated and how can it reduce the development effort and improve system quality attributes?
- Is the amount of effort needed to do the implementation still within the guideline?

## **Example 1: Care-AI Telemedicine Enhancement Multi-Agent System**

The document provides details for one primary project example, the **Care-AI telemedicine enhancement multi-agent system**, and outlines the **success criteria** for such projects in a second section.

This project focuses on a regional virtual clinic aiming to streamline triage, improve patient education, and reduce repetitive workloads.

- **Problem Description:** The system uses specialized AI agents to collaborate and support patients before and after online consultations.
- **Key Agent Roles:**
  - **Triage Agent:** Collects symptoms and classifies urgency levels.
  - **Preparation Agent:** Guides patients in preparing for consultations (e.g., medication lists, blood pressure logs).
  - **Education Agent:** Answers common questions using vector-based medical information retrieval.
  - **Follow-up Agent:** Provides post-consultation advice and reminders.
  - **Escalation Agent:** Monitors conversations and flags safety-critical cases for human intervention.
- **System Features:**
  - Agents coordinate via shared memory or messaging.
  - Each agent demonstrates autonomy through reasoning, planning, and tool use.
  - The system maintains logs for traceability and explainability.
- **Emphasis:** The focus is on demonstrating agentic behavior, explainable and responsible AI practices, AI-specific security, and sound engineering principles (e.g., MLSecOps/LLMSecOps).

### **Typical Project Requirements (Success Criteria)**

While labeled "Example 2," this section details the required deliverables and criteria for a successful project submission:

- **Presentation Slides:** Must clearly outline the problem context, agent roles, system overview, and a demo walkthrough.
- **System Architecture Document:** Must cover logical and physical architecture, infrastructure, data flow, and technology justifications.
- **Agent Design Documentation:** Details internal logic, reasoning patterns, planning loops, memory mechanisms, and autonomy.
- **Explainable and Responsible AI Report:** Explains considerations for fairness, bias mitigation, governance, and alignment with AI principles.
- **AI Security Risk Register:** Identifies risks like prompt injection or hallucinations and outlines mitigation strategies.
- **MLSecOps / LLMSecOps Pipeline Design:** Specifies tools and workflows for CI/CD, versioning, monitoring, and automated security testing.
- **Source Code Repository:** Shows modular agent implementation with documented, well-structured code.
- **Testing Artifacts:** Includes unit, end-to-end, and AI security tests.
- **UI Prototype:** A simple web or form-based interface to demonstrate multi-agent orchestration.
