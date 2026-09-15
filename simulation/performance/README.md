# Module 12 — Performance Evaluation

**Team PHARO — SIH26169**

## Purpose
Evaluates coarse alignment accuracy, acquisition latency, jitter suppression, and communication link availability against benchmark criteria.

## Planned Evaluation Metrics
- **Time to Initial Acquisition (TTA)**: Seconds elapsed from simulation start to first stable lock.
- **Root Mean Square Error (RMSE)**: Boresight pointing error RMS in microradians / arcseconds.
- **Circular Error Probable (CEP)**: CEP50 and CEP95 pointing error radius.
- **Link Availability**: Percentage of operational time that the beacon spot remains within fine-tracking handover window.
- **Re-acquisition Success Rate**: Percentage of dropouts successfully recovered without requiring full spiral scan.
