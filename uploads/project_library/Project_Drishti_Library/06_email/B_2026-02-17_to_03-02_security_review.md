FICTIONAL HACKATHON MATERIAL. All names, numbers and events are invented.

**From:** Farhan Siddiqui <farhan.s@ardentcement.example>
**To:** Neha Sharma
**Cc:** Lokesh Jain
**Date:** Tue, 17 Feb 2026 18:40
**Subject:** RE: PredCo security pack — Drishti

Neha,

Reviewed. Three blockers:

1. Your architecture shows the edge server pulling model updates from your registry. Not acceptable. No egress. Updates come on encrypted media through our change process, or through the jump host.
2. "Vendor support via VPN" — no. Jump host only, session recorded, access approved per session by my team.
3. Alert snapshots go to WhatsApp. That means images of our people leave the network through a phone. Explain how.

Your SOC 2 report is for your cloud product. What applies to on-prem?

Farhan

---

**From:** Neha Sharma
**To:** Farhan Siddiqui
**Date:** Thu, 19 Feb 2026 11:25
**Subject:** RE: PredCo security pack — Drishti

Hi Farhan,

Thank you — fair points.
1. Removed. Updates delivered as signed packages through your jump host; your team runs the install. Revised diagram attached.
2. Agreed. Jump host only. We'll follow your session approval process.
3. Option A: WhatsApp messages carry text only ("No helmet, Packer 2B, 10:42"), and the snapshot opens on the console inside the plant network. Option B: snapshot with faces blurred. We recommend A.

On SOC 2: our report covers the company's controls (access, change management, incident response, people). For on-prem we add a deployment checklist mapped to ISO 27001 Annex A controls. Sending it separately.

Neha

---

**From:** Farhan Siddiqui
**Date:** Mon, 2 Mar 2026 10:05
**Subject:** RE: PredCo security pack — Drishti

Option A approved. Checklist reviewed, two comments resolved. Cleared from IT-OT for PoC. Plant-wide will need a re-review.

Farhan
