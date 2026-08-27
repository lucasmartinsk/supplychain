# Vendor Risk Scoring and Treatment Standard

## 1. Purpose

This Standard defines a consistent, proportionate and explainable method for assessing ICT third-party services, evaluating control effectiveness, determining residual risk and selecting the appropriate risk treatment.

In simple terms, it explains how the Institution decides:

- how important a third-party service is;
- how much risk exists before controls are considered;
- whether the controls and evidence are adequate;
- how much risk remains;
- who must review, accept or escalate the result; and
- how frequently the relationship must be monitored.

This is a simulated standard created for an educational banking-oriented TPRM lab. It is not the policy or methodology of any named financial institution.

## 2. Scope

This Standard applies to ICT third-party service providers and, where relevant, their subcontractors supporting services used by the Institution.

The methodology applies throughout the relationship lifecycle, including:

- initial assessment and due diligence;
- onboarding and contracting;
- ongoing monitoring;
- material changes;
- incident and finding management;
- renewal; and
- termination and exit.

## 3. Guiding Principles

Assessments performed under this Standard shall follow these principles:

1. **Proportionality:** higher-impact and higher-risk relationships receive more rigorous assessment and oversight.
2. **Separation of criticality and risk:** service importance does not automatically mean that a vendor is poorly controlled.
3. **Evidence-based decisions:** ratings shall be supported by current, relevant and traceable information.
4. **No assumptions from missing data:** unavailable information shall be recorded as `Review Required`, not scored as zero or treated as satisfactory.
5. **No automatic penalties from labels:** workflow status, contract dates or the existence of a past incident shall not increase risk without an assessment of the actual exposure.
6. **No double counting:** the same underlying issue shall not be scored repeatedly across different factors.
7. **Human oversight:** calculated results may be challenged or overridden when material circumstances are not adequately represented by the methodology.
8. **Time-bound acceptance:** risk acceptance and exceptions shall have an owner, justification, expiry date and review date.
9. **Sustainable remediation:** corrective action should address both the immediate gap and, where relevant, the cause of recurrence.

## 4. Roles and Responsibilities

Responsibilities are defined by function because organisational placement may differ between institutions.

| Role | Typical responsibility |
|---|---|
| **Vendor** | Implements vendor-owned remediation and provides evidence. |
| **Relationship Owner — First Line** | Owns the relationship, coordinates due diligence, monitors performance and follows up remediation. |
| **Subject-Matter Expert** | Assesses evidence within areas such as cybersecurity, privacy, resilience, legal or financial risk. |
| **Independent Risk Oversight — Second Line** | Defines standards, provides oversight and challenge, monitors material exceptions and reviews higher-risk decisions. |
| **Risk Acceptance Authority** | Formally accepts residual risk within delegated authority. |
| **Risk Committee** | Decides material cases, extraordinary exceptions and exposures outside risk appetite. |
| **Internal Audit — Third Line** | Independently assesses whether the TPRM framework and its controls operate effectively. |

Independent Risk Oversight is not required to review every item of evidence. The depth of challenge shall reflect service criticality, finding severity and residual risk.

## 5. Assessment Model

The assessment produces five visible outputs:

1. `Criticality Tier`
2. `Inherent Risk`
3. `Control Effectiveness`
4. `Residual Risk`
5. `Risk Treatment`

The methodology does not use a single universal `0–100` vendor score. Supporting points are used only to make classifications consistent and traceable.

## 6. Criticality Tier

### 6.1 Objective

Criticality measures the potential impact on the Institution and its customers if the service becomes unavailable, fails or cannot be replaced.

Criticality does not assess whether the vendor's controls are good or bad and shall not be added directly to the residual risk calculation.

### 6.2 Criticality Factors

Each factor is rated from `0` to `3`.

| Factor | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Service interruption** | No meaningful impact | Minor disruption | Important operation affected | Critical function interrupted |
| **Customer impact** | No customer impact | Limited impact | Significant customer impact | Essential financial service affected |
| **Regulatory importance** | No material relevance | Low relevance | Material obligation may be affected | Critical or important function / material obligation affected |
| **Substitutability and exit** | Immediately replaceable | Easily replaceable | Replacement is difficult | No viable short-term alternative |

### 6.3 Tier Classification

| Total | Criticality Tier |
|---:|---|
| `10–12` | **Tier 1 — Critical** |
| `7–9` | **Tier 2 — High Importance** |
| `4–6` | **Tier 3 — Moderate** |
| `0–3` | **Tier 4 — Low** |

The underlying result and rationale shall remain visible in the assessment record.

## 7. Inherent Risk

### 7.1 Objective

Inherent Risk represents the exposure arising from the proposed service before the effectiveness of controls is considered.

### 7.2 Inherent Risk Factors

Each factor is rated from `0` to `3` using documented vendor and service information.

| Factor | Assessment focus |
|---|---|
| **Data exposure** | Classification, sensitivity, volume, processing and storage of Institution or customer data. |
| **System access** | Connectivity, authentication, privileged access and ability to affect Institution systems. |
| **Customer and transaction exposure** | Customer interaction, transaction processing, volume and potential customer harm. |
| **Delivery exposure** | Delivery locations, operational dependency, concentration and service complexity. |
| **Fourth-party exposure** | Use, importance, location and complexity of subcontractors supporting the service. |

The lab shall display the assigned points, source information and rationale for every factor.

### 7.3 Inherent Risk Classification

| Total | Inherent Risk |
|---:|---|
| `0–3` | **Low** |
| `4–7` | **Medium** |
| `8–11` | **High** |
| `12–15` | **Very High** |

Where a required factor cannot be assessed, the result shall show `Review Required`. The system shall not silently assign zero.

## 8. Control Assessment

### 8.1 Control Domains

Controls and evidence shall be assessed within the following domains when applicable:

- Information Security;
- Privacy and Data Protection;
- Operational Resilience;
- Fourth-Party Management;
- Contract and Exit; and
- Operational Performance and Incident Management.

Evidence requirements shall be proportionate to the service. A document or control that is not relevant shall not affect the result.

### 8.2 Evidence Status

| Evidence status | Assessment treatment |
|---|---|
| **Valid and relevant** | No gap. Scope, issuing entity and validity shall be confirmed. |
| **Pending within an agreed deadline** | Tracked without automatic adverse rating. Approval may remain conditional where the evidence is required before go-live. |
| **Pending overdue** | Finding severity determined by relevance, exposure and compensating controls. |
| **Expired with a valid temporary alternative** | Partial gap may apply until permanent evidence is provided. |
| **Expired without an adequate alternative** | Active finding. |
| **Missing** | Active finding when the evidence is applicable and required. |

The presence of a certification or report does not automatically demonstrate control effectiveness. Its relevance, scope, date, exceptions and relationship to the assessed service shall be considered.

## 9. Finding Severity

Finding severity shall be based on actual exposure rather than the finding label alone.

The assessment shall consider:

- Criticality Tier;
- relevance of the affected control;
- data and system exposure;
- potential impact on customers and continuity;
- compensating controls;
- duration of exposure;
- recurrence or systemic weakness;
- active incidents; and
- remediation status.

| Severity | Definition |
|---|---|
| **Low** | Limited gap with no material exposure and straightforward remediation. |
| **Medium** | Relevant weakness with controlled impact or adequate compensating controls. |
| **High** | Material deficiency that may affect sensitive data, service continuity, compliance or customers. |
| **Critical** | Immediate or unacceptable exposure, severe active incident or risk outside appetite. |

A certificate expiry, contract date, workflow status or historical incident shall not automatically determine severity.

## 10. Specific Assessment Rules

### 10.1 Fourth-Party Risk

An undeclared subcontractor always creates a transparency concern, but its severity shall reflect the subcontractor's actual role.

The assessment shall consider whether the fourth party:

- supports a critical or important part of the service;
- accesses Institution or customer data;
- can affect service continuity;
- creates concentration or location risk; and
- is subject to appropriate contractual and monitoring arrangements.

Lack of sufficient information shall result in `Review Required` and a request for clarification, not an automatic assumption of the worst possible scenario.

### 10.2 Contract and Exit

A contract approaching expiry shall not increase risk solely because of the remaining number of days.

A finding may arise where there is an actual issue, including:

- renewal is not progressing within the required timeline;
- required contractual protections are missing;
- termination rights are inadequate;
- an exit plan is absent or not viable;
- transition creates unacceptable continuity risk; or
- data return and deletion arrangements are insufficient.

### 10.3 Operational Performance and Incidents

Workflow labels such as `Under Review` or `Terminated` shall not automatically change the rating.

Incident assessment shall consider:

- severity and duration;
- services, systems, data and customers affected;
- detection and containment time;
- time taken to notify the Institution;
- compliance with contractual and regulatory obligations;
- root-cause analysis;
- remediation quality and timeliness; and
- recurrence.

A historical incident that was appropriately communicated, contained and sustainably remediated does not require a permanent adverse rating. It may remain relevant to monitoring frequency and trend analysis.

## 11. Control Effectiveness

Control Effectiveness reflects the overall ability of the relevant controls to manage the identified exposure.

| Open findings | Control Effectiveness |
|---|---|
| No material open findings | **Effective** |
| Only Low or Medium findings, with no systemic weakness | **Mostly Effective** |
| One High finding or multiple related Medium findings | **Partially Effective** |
| One Critical finding or multiple systemic High findings | **Ineffective** |

Aggregation requires judgement. The methodology shall not treat an unrelated count of findings as automatically equivalent to a systemic control failure.

## 12. Residual Risk

Residual Risk is determined by combining Inherent Risk and Control Effectiveness.

| Inherent Risk | Effective | Mostly Effective | Partially Effective | Ineffective |
|---|---|---|---|---|
| **Low** | Low | Low | Medium | High |
| **Medium** | Low | Medium | High | High |
| **High** | Medium | High | High | Critical |
| **Very High** | High | High | Critical | Critical |

Criticality Tier remains visible and determines oversight requirements but is not added to this matrix as a penalty.

## 13. Human Override

The calculated Residual Risk may be overridden where a material circumstance is not adequately represented by the standard methodology.

An override shall record:

- calculated rating;
- final rating;
- reason and supporting evidence;
- approving authority;
- effective date;
- expiry or review date; and
- conditions for removal.

Examples include an active severe incident, emerging regulatory restriction, material customer impact or a concentration exposure requiring immediate attention.

An override shall not be removed automatically. The relevant evidence and residual exposure shall be reassessed.

## 14. Remediation and Finding Closure

The standard remediation workflow is:

1. identify and document the finding;
2. determine severity and current exposure;
3. assign a Remediation Action Plan, owner and due date;
4. implement immediate correction where necessary;
5. address root cause and recurrence where relevant;
6. submit the required evidence;
7. validate implementation and sustainability;
8. close, return or escalate the finding; and
9. continue monitoring for recurrence where appropriate.

A promise or the creation of a plan does not reduce the assessment result. Reduction requires evidence that the relevant exposure has been adequately addressed.

A corrected immediate gap may reduce the associated finding severity while a related control remains `Partially Effective` if sustainable remediation has not yet been demonstrated.

## 15. Risk Treatment

Available treatments are:

| Treatment | Application |
|---|---|
| **Mitigate** | Implement corrective, preventive, technical, operational or contractual controls. |
| **Accept** | Formally accept residual risk within delegated authority. |
| **Avoid** | Do not onboard, renew or continue the relationship. |
| **Transfer** | Transfer part of the financial or contractual impact through insurance, indemnity or other mechanisms. Transfer does not eliminate operational or regulatory responsibility. |
| **Monitor** | Apply enhanced observation while the exposure, remediation or external situation develops. |

### 15.1 Expected Treatment by Rating

| Residual Risk | Expected response |
|---|---|
| **Low** | Approval and normal monitoring. |
| **Medium** | Approval may proceed with proportionate remediation where required. |
| **High** | Conditional approval, formal remediation, enhanced monitoring and acceptance by an appropriately senior authority. |
| **Critical** | Avoid, suspend or escalate for an extraordinary, time-bound exception. |

### 15.2 Risk Acceptance

Risk acceptance shall include:

- description of the residual exposure;
- business justification;
- Risk Acceptance Authority;
- compensating controls;
- applicable remediation;
- approval date;
- expiry date; and
- reassessment date.

Acceptance is not permanent and shall not be used to avoid remediation where the exposure is outside risk appetite.

### 15.3 Temporary Continuity Exception

Immediate termination may create greater operational or customer harm than temporary continuation. Where a critical service has no viable short-term alternative, a time-bound exception may be considered with:

- documented comparison of continuation and termination risk;
- compensating controls;
- remediation milestones;
- enhanced monitoring;
- tested or credible exit and transition plan;
- clear termination triggers; and
- approval by the appropriate Risk Committee.

## 16. Monitoring and Reassessment

### 16.1 Criticality-Based Frequency

| Criticality Tier | Full assessment | Routine monitoring |
|---|---|---|
| **Tier 1 — Critical** | Annual | Quarterly |
| **Tier 2 — High Importance** | Every 12–18 months | Semi-annual |
| **Tier 3 — Moderate** | Every 24 months | Annual |
| **Tier 4 — Low** | Every 36 months | Event-driven |

### 16.2 Residual-Risk-Based Frequency

| Residual Risk | Monitoring |
|---|---|
| **Critical** | Continuous or monthly, with committee oversight |
| **High** | Quarterly |
| **Medium** | Semi-annual |
| **Low** | Annual |

The stricter applicable frequency shall be used.

### 16.3 Event-Driven Reassessment

An assessment shall be reviewed outside the normal cycle when relevant events occur, including:

- material incident;
- material service or technology change;
- new material fourth party;
- change in data location or processing;
- financial deterioration;
- material or overdue remediation;
- significant contractual change;
- relevant regulatory change;
- merger, acquisition or change of control; or
- credible information indicating a change in exposure.

## 17. Transparency and Explainability

For each vendor, the lab shall display:

- Criticality Tier and factor rationale;
- Inherent Risk factor values, points and source information;
- applicable control domains and evidence status;
- open findings and severity rationale;
- Control Effectiveness;
- Residual Risk matrix result;
- any human override;
- Risk Treatment;
- acceptance, remediation and monitoring dates; and
- responsible roles.

Ratings shall not rely on colour alone. Text labels and numerical values shall be shown to support accessibility and auditability.

### 17.1 Example Calculation

| Inherent Risk factor | Vendor information | Points | Rationale |
|---|---|---:|---|
| Data exposure | Personal and confidential data | 3 | Sensitive customer data is processed. |
| System access | Standard authenticated connection | 2 | Vendor connects to Institution systems without privileged administration. |
| Customer and transaction exposure | Supports customer operations | 2 | Disruption may affect customers. |
| Delivery exposure | Important operational dependency | 2 | Replacement requires preparation. |
| Fourth-party exposure | Limited declared subcontracting | 1 | One declared subcontractor supports a non-critical component. |
| **Total** |  | **10/15** | **High Inherent Risk** |

Example final result:

```text
Criticality:               Tier 1 — Critical
Inherent Risk:             High
Control Effectiveness:     Partially Effective
Calculated Residual Risk:  High
Human Override:            None
Final Residual Risk:       High
Treatment:                 Mitigate
Monitoring:                Quarterly
```

## 18. AI-Assisted Recommendations

Where the lab uses an AI assistant, the assistant shall:

- receive only the minimum vendor data required for the task;
- use approved regulatory, standards and simulated internal-policy context;
- explain which assessment facts support its recommendation;
- avoid inventing missing vendor information;
- label uncertainty and request human review;
- never independently accept risk, close findings or change final ratings; and
- retain human decision-making and approval.

AI output is advisory and shall not replace accountable review, challenge or approval.

## 19. Governance and Review

This Standard should be reviewed at least annually and following material regulatory, methodology or risk-appetite changes.

Methodology changes shall be documented, tested and approved before implementation. Historical assessments should be reviewed where a change could materially affect their result.

## 20. References

- Regulation (EU) 2022/2554 on digital operational resilience for the financial sector (DORA), particularly the proportional management of ICT third-party risk and the continued responsibility of financial entities.
- European Banking Authority Guidelines on outsourcing arrangements.
- Interagency Guidance on Third-Party Relationships: Risk Management, issued by the Board of Governors of the Federal Reserve System, Federal Deposit Insurance Corporation and Office of the Comptroller of the Currency.

