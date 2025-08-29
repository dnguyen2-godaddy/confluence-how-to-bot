# Dashboard Documentation Template

Use this comprehensive template to create professional, structured documentation for your dashboards. This template follows industry best practices and ensures consistency across all dashboard documentation.

## 1. Dashboard Name & High-Level Summary

**Dashboard Title:**
[Enter the official dashboard title]

**Short Description:**
[Provide 2-3 sentences about what this dashboard does and why it's useful]

**Link to Dashboard:**
[Dashboard URL]

**Example:**
Dashboard Title: "Customer Acquisition Trends"
Short Description: This dashboard tracks how many new customers we gain daily, weekly, and monthly, including where they come from.
Link to Dashboard: [Dashboard URL]

## 2. Purpose & Business Context

**Business Questions This Dashboard Answers**
- [E.g., "How many new customers did we gain last month?"]
- [E.g., "Which marketing channel drives the most acquisitions?"]
- [E.g., "What was my cohort renewal rate for M365 last month?"]

**Key Use Cases**
- [E.g., Domain renewal analysis, marketing ROI analysis, etc.]
- [Add more use cases as needed]

**Domains**
- [E.g., Care, Customer Market, Finance, Domains]

## 3. Dashboard Views

### [View Name]

**Description**
[Describe what this view displays and its purpose]

**Key Metrics in View**
- **Metric / Definition:** [Short version, full version can be listed in Section 4. Key Metric Definitions]

**Intended Audience/Use Case**
[E.g., Care, Customer Market, Finance, Domains]

**Navigation Walkthrough**
[E.g., Use date granularity filter to choose weekly or monthly view]

**Common Workflows & Tips**
- [E.g., Maximize individual charts for clearer trend inspection]
- [E.g., Set your window to 90% for improved viewing]

## 4. Key Metric Definitions

| Metric | Definition / Description | Data Governance Link | Calculation Logic / Notes |
|--------|-------------------------|---------------------|---------------------------|
| [Metric Name] | [Full definition of metric] | [Alation DG Link (if applicable)] | [Data source, FAQs, etc.] |

## 5. Data Refresh & Update Cadence

**Schedule:** [E.g., "Daily at 3:00 AM UTC"]
**Data Pipeline:** [E.g., "ETL pipeline from bill_line"]
**Dependencies:** 
- [List any dependencies]

## 6. Ownership & Contacts

**Primary Owner:** [Name or team (e.g., "Analytics Team – John Doe, Slack handle @john_doe")]
**Slack Channel:** [#channel-i-go-to-with-questions]
**Stakeholders:** [E.g., "USI," "Finance"]

## 7. Known Limitations & Assumptions

**Limitations**
- [E.g., "Does not include 123-Reg customers"]

**Workarounds**
- [E.g., "For pre-2020 data, refer to the archival 'Legacy Acquisition Dashboard.'"]

## 8. Frequently Asked Questions (FAQ)

**Question:** [E.g., "Do this dashboard use cohort or cash basis for renewal rate?"]
**Answer:** [E.g., "This dashboard uses cohort logic for renewal rate."]

**Question:** [E.g., "Who do I talk to about adding a new filter?"]
**Answer:** [E.g., "Reach out to the Analytics Data Team via Slack #data-integrations."]

*Why this helps RAG: When an internal user asks a question ("Where is LinkedIn data?"), your retrieval system can bring up the relevant FAQ chunk.*

## 9. Relevant Links / References

**Related Dashboards:** [E.g., "Marketing Spend Dashboard," "Customer Retention Dashboard"]
**Documentation on Data Sources:** [E.g., Confluence page for bill_line, etc.]
**Training / Video Tutorials:** [If available]

## 10. Change Log & Version History

| Date | Change Description | Jira | Changed By | Requester |
|------|-------------------|------|------------|-----------|
| [Date] | [E.g., created month over month trending views] | [JIRA-123] | [Your Name or Team] | [Requester] |

*Keeping a historical record helps advanced users troubleshoot or see whether changes might affect their analysis.*

---

## Template Usage Notes

- **Copy this template** for each new dashboard
- **Customize sections** based on your specific dashboard needs
- **Keep it updated** as dashboards evolve
- **Share with stakeholders** for feedback and validation
- **Use consistent formatting** across all documentation
- **Include screenshots** where helpful for clarity
- **Link to related resources** for comprehensive coverage

## Best Practices

1. **Be Specific:** Use exact metric names, filter options, and navigation steps
2. **Think Like a User:** Document what someone new to the dashboard needs to know
3. **Keep It Current:** Update documentation when dashboards change
4. **Include Examples:** Provide real-world scenarios and use cases
5. **Make It Actionable:** Users should know what to do with the information
6. **Consider Accessibility:** Use clear language and logical structure
