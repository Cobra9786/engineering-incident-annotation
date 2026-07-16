# Project Story: Northstar Fluid Systems
Your theoretical assignment

You are hired by Northstar as an Applied AI Engineer.

Its operations director explains:

We receive too many pressure alarms. Some are real leaks, some are failing sensors, some are setup errors, and some require an immediate shutdown. Our experienced technicians can usually tell the difference, but the information is scattered across sensor readings and maintenance notes. We want an AI-assisted triage system that organizes the evidence, recommends the next step, and escalates dangerous incidents without pretending to know more than the available data supports.

Your job is not initially to build an autonomous repair agent.

Your first responsibility is to establish a reliable ground-truth and evaluation system.

You must:

Interview domain experts.
Define the incident taxonomy.
Create annotation guidelines.
Annotate representative incidents.
Document ambiguous cases.
Build validation rules.
Establish held-out test cases.
Evaluate whether an AI model can extract the correct structured result.
Measure unsafe failure modes.
Require human approval before operational action.
Why the first 20 incidents matter

The first 20 records are not intended to train a useful production model.

They are intended to validate the problem definition.

We are testing whether the annotation contract can represent:

true leaks
sensor failures
pump failures
cavitation
valve-position errors
blockages
normal depressurization
maintenance-related changes
contradictory evidence
unknown causes
immediate shutdown cases
cases where the system must abstain

Once those distinctions are stable, the dataset can grow to 100, 500, or several thousand records.

## Business Context

Northstar Fluid Systems is a fictional industrial service company that operates and maintains fluid-transfer and hydraulic equipment across processing plants, water-treatment facilities, chemical sites, and remote pumping stations.

Its customers depend on pumps, pipelines, valves, tanks, filters, hydraulic power units, and control systems to operate continuously and safely.

Northstar receives large volumes of operational information from:

* pressure sensors
* flow sensors
* fluid-level sensors
* temperature sensors
* vibration sensors
* valve-position sensors
* motor and controller telemetry
* SCADA alarms
* operator logs
* maintenance tickets
* technician reports

The company already has threshold-based monitoring. It can detect conditions such as low pressure, high temperature, or reduced flow.

However, a threshold alarm does not explain why the condition occurred.

A low-pressure event may indicate:

* a pump seal leak
* a pipeline leak
* cavitation
* an obstructed inlet
* an incorrectly positioned valve
* a low reservoir
* worn pump components
* incorrect motor speed
* a failed pressure sensor
* loose sensor wiring
* expected depressurization
* a maintenance configuration error
* insufficient evidence to determine a cause

Treating every low-pressure warning as a leak creates false alarms, unnecessary shutdowns, and wasted maintenance effort. Treating every warning as harmless risks equipment damage, environmental release, production loss, or a safety incident.

## The Operational Problem

Northstar’s experienced technicians can often distinguish these cases by combining several sources of information.

For example, a technician may compare:

* pump inlet and discharge pressure
* measured flow
* fluid level
* motor current
* vibration
* temperature
* valve position
* recent maintenance
* visible evidence
* operator observations

This reasoning is currently inconsistent and difficult to scale. Important evidence is distributed across multiple systems, and less-experienced personnel may reach different conclusions from the same incident.

Northstar wants an AI-assisted incident-triage platform that can organize this information into a structured and reviewable recommendation.

## The Assignment

An Applied AI Engineer is hired to design the Engineering Incident Intelligence and Evaluation Platform.

The initial goal is not autonomous equipment control.

The first goal is to create a reliable ground-truth and evaluation foundation that can answer:

* Which component appears to be affected?
* What failure mode is supported by the evidence?
* How severe is the incident?
* How urgently should personnel respond?
* What is the probable cause?
* Which observations support that probable cause?
* What action should be proposed?
* Is there enough evidence to make a reliable classification?
* Must a human review the incident?

## Example Incident

Input report:

> Pump P-104 discharge pressure oscillated between 70 and 110 psi. A rattling sound was heard near the inlet. Reservoir level was below minimum. No external leak was visible.

Expected structured annotation:

```json
{
  "incident_id": "INC-0004",
  "component": "pump",
  "failure_mode": "cavitation",
  "severity": "high",
  "urgency": "immediate",
  "probable_cause": "insufficient inlet fluid supply",
  "evidence": [
    "discharge pressure oscillated between 70 and 110 psi",
    "rattling sound was heard near the inlet",
    "reservoir level was below minimum"
  ],
  "recommended_action": "stop the pump, restore fluid level, and inspect the inlet path",
  "confidence": 0.95,
  "abstain": false,
  "requires_human_review": true
}
```

The system does not classify this incident as a leak merely because pressure is low. The combination of pressure oscillation, inlet noise, and low reservoir level supports cavitation.

## Evidence-Grounded Classification

Every classification must be tied to evidence contained in the incident report or retrieved from an approved source.

The system must distinguish among cases such as:

### Physical leak

Pressure falls and visible fluid is found near a seal or line.

### Instrumentation fault

An electronic sensor reports pressure loss while a redundant mechanical gauge remains stable.

### Operational configuration problem

Pressure changes after maintenance because a valve, bypass, controller setting, or pump speed is incorrect.

### Mechanical or hydraulic failure

Pressure behavior is accompanied by evidence such as vibration, abnormal noise, overheating, flow loss, or visible damage.

### Ambiguous incident

Pressure is outside the expected range, but the available evidence does not establish a responsible component or probable cause.

For ambiguous incidents, the correct result is abstention and human review—not an invented diagnosis.

## Human-in-the-Loop Requirement

The platform may propose classifications and recommended actions, but it must not autonomously perform high-risk operational actions.

Human approval is required before:

* shutting down production equipment
* changing control settings
* opening or closing process valves
* dispatching emergency personnel
* creating a critical escalation
* approving equipment restart
* initiating maintenance that affects safety or production

The AI system assists human judgment; it does not replace operational authority.

## Evaluation Goals

The platform will compare multiple approaches:

1. prompt-only structured extraction
2. retrieval-augmented generation
3. a LoRA-adapted model
4. an optional quantized local model

Evaluation will measure:

* JSON validity
* schema compliance
* field-level accuracy
* failure-mode classification accuracy
* severity accuracy
* false escalation rate
* missed critical-incident rate
* hallucinated evidence rate
* abstention precision
* abstention recall
* reviewer disagreement
* latency
* inference cost

Aggregate accuracy alone is not sufficient. A model that fabricates evidence or misses critical incidents is unsafe even if most ordinary classifications are correct.

## First Milestone

The first milestone creates 20 pressure-related incidents covering:

* physical leaks
* pressure-sensor failures
* signal loss
* calibration drift
* pump cavitation
* inlet blockage
* outlet blockage
* incorrect valve position
* low reservoir level
* normal depressurization
* maintenance errors
* contradictory sensor readings
* unknown probable causes
* emergency conditions
* abstention cases

These initial examples establish and test the annotation contract. They are not presented as a production-scale training dataset.

## Long-Term Platform

After the ground-truth layer is stable, the project will add:

* prompt-only model inference
* structured prediction storage
* retrieval of similar incidents
* retrieval of component documentation
* LoRA fine-tuning
* model comparison
* FastAPI services
* PostgreSQL storage
* authentication
* audit records
* observability
* human approval workflows
* a Rust ingestion or reliability component
* optional small-model deployment on constrained or edge hardware

The completed platform will demonstrate the full lifecycle of an Applied AI system: domain analysis, data design, annotation, evaluation, model adaptation, human review, deployment, and production reliability.
