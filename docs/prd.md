# ALIBI — Product Requirements Document (PRD)

**Version:** 1.0  
**Status:** Phase 1 — Product Requirements Finalized  
**Product:** Alibi  
**Platform:** Mobile Application  
**Initial Release:** Balanced MVP  
**Total Product Decisions:** 20/20 Finalized

---

# 1. Product Overview

## 1.1 Product Concept

Alibi is an AI-powered, story-driven interrogation game where players face intelligent AI detectives and attempt to convince them of their innocence or avoid getting caught.

Players participate in fictional investigations involving crimes, social mysteries, and psychological thrillers.

The AI detective must remember previous statements, analyze evidence, identify contradictions, develop interrogation strategies, and respond dynamically to the player's actions.

The experience should feel like a psychological battle of intelligence between the player and the detective.

## 1.2 Core Product Vision

**Build an interrogation game where the detective genuinely investigates the player instead of simply responding to messages.**

Alibi is not intended to be a basic AI chatbot with a detective personality.

The game must combine:

- Intelligent, stateful AI interrogation.
- Persistent memory and contextual reasoning.
- Strategic deception and persuasion.
- Evidence-based investigation.
- Dynamic player-driven outcomes.
- Immersive storytelling.
- Memorable detective personalities.
- Meaningful replayability and progression.

## 1.3 Primary Gameplay Hook

**Can you outsmart an intelligent AI detective and get away with your story?**

The primary experience focuses on guilty suspects attempting to avoid getting caught.

However, the game also supports innocent suspects attempting to prove their innocence.

---

# 2. Finalized Product Decisions

This section is the authoritative record of the 20 decisions made during Phase 1.

## Decision 1 — Player Roles

**Selected: Both guilty and innocent roles, with guilty-focused gameplay as the primary experience.**

- Players may be guilty or innocent depending on the case.
- Guilty players must construct convincing defenses and avoid getting caught.
- Innocent players must overcome suspicion and establish credible explanations.
- Guilty-suspect gameplay is the primary product hook.
- The initial ratio of guilty to innocent cases has not been finalized.

## Decision 2 — Player Freedom

**Selected: Hybrid Freedom.**

- Players receive predetermined case facts and character backgrounds.
- Players have relevant private information.
- Players freely construct their defenses and explanations.
- Players can lie, bluff, conceal information, improvise, or tell the truth.
- The AI must respond to player-generated explanations rather than relying on predefined dialogue paths.

## Decision 3 — Detective Personality

**Selected: Adaptive Detective with a cocky and sarcastic personality.**

- The detective adjusts its interrogation tactics to the player's behavior.
- It may become friendly, skeptical, aggressive, or calculating.
- It should be intelligent, witty, slightly arrogant, and sarcastic.
- Sarcasm should be situational rather than constant.
- Cinematic verdict dialogue must include the detective's personality.
- The detective should remain sarcastic even when the player wins.
- Personality must not compromise the fairness or accuracy of the investigation.

## Decision 4 — Suspicion System

**Selected: Hybrid Suspicion Meter.**

During gameplay, players see qualitative suspicion levels:

- Low
- Moderate
- High
- Critical

The exact numerical suspicion score remains hidden until the final verdict.

Suspicion must reflect validated investigation findings and player behavior, rather than arbitrary LLM-generated values.

## Decision 5 — Verdict System

**Selected: Dynamic Combined Verdict System.**

The outcome considers:

- Available evidence.
- Consistency of the player's statements.
- Credibility of explanations.
- Persuasion and successful defenses.
- Unresolved contradictions.
- Reasonable doubt and alternative explanations.

The outcome must not be predetermined solely by the original case plot.

Players must have a meaningful opportunity to influence the outcome through their decisions and arguments.

A guilty player can successfully escape suspicion. An innocent player can fail to convince the detective.

## Decision 6 — Interrogation Length

**Selected: Adaptive Interrogation Length by Difficulty.**

| Difficulty   | Target Turns | Estimated Duration |
| ------------ | ------------ | ------------------ |
| Rookie       | 5–7          | 3–5 minutes        |
| Intermediate | 8–12         | 5–10 minutes       |
| Expert       | 12–18        | 10–15 minutes      |

The detective may reach a justified conclusion early when sufficient grounds exist.

The game should avoid unnecessarily prolonging interrogations.

## Decision 7 — Case Information

**Selected: Partial Knowledge with Hidden Detective Evidence.**

Players know:

- Their character's background.
- Whether they are guilty or innocent.
- Relevant personal events and facts.
- Their private information.

The detective has access to its established investigation file, which may include evidence unknown to the player.

Evidence can be revealed strategically during interrogation.

**Critical rule:** Evidence must exist in the canonical case data before gameplay begins. The detective cannot invent evidence to trap the player.

## Decision 8 — Evidence Interaction

**Selected: Limited Evidence Interactions.**

Players can:

- Inspect evidence available to them.
- Review accessible documents and records.
- Request specific evidence verification.
- Reference evidence in their defense.
- Challenge the detective's interpretations.

Evidence checks must operate against established case data.

Full independent crime-scene investigation is not required for the MVP.

## Decision 9 — Replayability

**Selected: Dynamic Case Variations.**

The same case can have multiple validated variations.

Variations may change:

- Witness details.
- Evidence availability.
- Timeline details.
- Relevant circumstances.
- Detective interrogation strategies.

The core mystery remains recognizable.

Every variation must have internally consistent facts established before interrogation begins.

## Decision 10 — Difficulty System

**Selected: Adaptive AI Intelligence Difficulty.**

Higher difficulty means more sophisticated interrogation strategies.

| Attribute               | Rookie   | Intermediate  | Expert                  |
| ----------------------- | -------- | ------------- | ----------------------- |
| Memory accuracy         | Accurate | Accurate      | Accurate                |
| Contradiction detection | Reliable | Reliable      | Reliable                |
| Questioning             | Direct   | Strategic     | Multi-step strategies   |
| Evidence disclosure     | Earlier  | Selective     | Carefully timed         |
| Follow-up depth         | Basic    | Context-aware | Deep and interconnected |
| Psychological pressure  | Low      | Moderate      | High                    |
| Interrogation turns     | 5–7      | 8–12          | 12–18                   |

Lower difficulties must not artificially disable memory or basic reasoning.

## Decision 11 — Final Verdict Experience

**Selected: Detailed Case Breakdown + Cinematic Detective Monologue.**

Each completed interrogation includes:

- Final outcome.
- Dramatic, personalized detective monologue.
- Sarcastic remarks regardless of victory or defeat.
- Exact final suspicion score.
- Successful defenses.
- Important contradictions.
- Missed opportunities.
- Performance rating.
- Shareable result card.

The monologue should reference actual interrogation events rather than use a generic script.

## Decision 12 — Detective Characters

**Selected: Multiple Detectives + Unlockable Detectives.**

The initial release contains exactly two detective personalities.

- One detective is available by default.
- The second detective is unlockable through progression.
- Detectives have distinctive personalities and interrogation strategies.
- Additional detectives can be introduced in future updates.

Both detectives share the same underlying investigation and fairness requirements.

**Proposed launch archetypes, not finalized character identities:**

1. **The Showman:** Cocky, witty, sarcastic, psychologically confrontational.
2. **The Strategist:** Calm, observant, calculating, patient, and subtly intimidating.

Final names, visual designs, and detailed character backgrounds remain open.

## Decision 13 — Player Progression

**Selected: Combined XP, Ranks, and Unlockable Content.**

The progression system includes:

- Experience points.
- Player ranks.
- Case progression.
- Detective unlocks.
- Achievements.
- Unlockable challenges and content.

Players should be rewarded for participating and improving, including when they lose an interrogation.

The exact rank names, XP formulas, and unlock thresholds are not finalized.

## Decision 14 — Daily Case Challenge

**Selected: Daily Case Challenge at Launch.**

- One featured case or validated variation is offered each day.
- Players can earn bonus XP.
- Daily participation and streaks are tracked.
- Special challenge objectives may be included.
- Existing validated case variations can be reused.
- Missing a day must not erase previously earned XP or rank.

Daily challenges are part of the initial MVP.

## Decision 15 — Monetization

**Selected: Hybrid Freemium.**

The monetization model includes:

- Free starter gameplay.
- Free daily challenges, subject to usage limits.
- Paid case packs.
- Optional interrogation credits.
- Free XP, rank, and core progression.

Players will not be charged for individual messages during an interrogation.

Interrogation credits apply at the session level.

Purchasing case content and consuming AI session allowances are separate concepts.

Subscriptions may be evaluated after launch, but are not required in the initial model.

Exact prices, allowances, and usage limits remain undecided.

## Decision 16 — Case Categories

**Selected: All Three Categories.**

**Traditional Crime Mysteries**

- Murder investigations.
- Robberies.
- Disappearances.
- Fraud.
- Other criminal investigations.

**Everyday and Social Mysteries**

- Workplace scandals.
- Relationship mysteries.
- Thefts.
- Humorous accusations.
- Social disputes.

**Psychological Thrillers**

- Betrayals.
- Hidden motives.
- Unreliable witnesses.
- Psychological manipulation.
- Unexpected revelations.

Categories can overlap within a case.

## Decision 17 — Story Presentation

**Selected: Hybrid Storytelling.**

Each case includes:

1. A short cinematic introduction.
2. An interactive case briefing.
3. The main interrogation experience.
4. Evidence reveals and story developments during gameplay.
5. A cinematic final verdict.

The storytelling should feel immersive without relying on expensive full-length cutscenes.

## Decision 18 — Player Control

**Selected: Strategic Player Actions Through Natural Dialogue.**

Players can:

- Challenge accusations.
- Request verification.
- Question witness credibility.
- Redirect conversations.
- Introduce alternative explanations.
- Bluff.
- Remain silent.
- Reveal or conceal information.

The AI must recognize the player's intent and adapt appropriately.

Players should not be forced to select predefined action buttons for every decision.

## Decision 19 — Game Session Persistence

**Selected: Automatic Save and Resume.**

Players can leave an unfinished interrogation and continue later.

The system must retain:

- Conversation history.
- Player claims.
- Structured AI memory.
- Contradictions.
- Evidence discoveries.
- Suspicion state.
- Remaining turns.
- Relevant investigation state.

The resumed interrogation must preserve context and continuity.

Multiple simultaneous active investigations are not required in the MVP.

## Decision 20 — MVP Scope

**Selected: Balanced MVP.**

The first public release will include:

- Five handcrafted cases.
- Validated case variations.
- Two detective personalities.
- Intelligent AI interrogation.
- Authentication and user profiles.
- Persistent game sessions.
- Evidence interactions.
- XP, ranks, achievements, and unlockable content.
- Daily Case Challenge.
- Cinematic introductions and verdicts.
- Dynamic scoring and detailed results.
- Basic hybrid freemium monetization.

The development team should build and validate one complete playable case before expanding to all five.

---

# 3. Core Player Journey

The expected player journey is:

**Step 1 — Launch Alibi**

The player opens the mobile application and authenticates or enters through an onboarding flow supported by the final authentication design.

**Step 2 — Select a Case**

The player chooses an available investigation based on its story, category, difficulty, and progression requirements.

**Step 3 — Cinematic Introduction**

A short narrative establishes the incident, atmosphere, and stakes.

**Step 4 — Case Briefing**

The player receives their character's background, role, known circumstances, and accessible information.

**Step 5 — Interrogation**

The AI detective begins questioning.

The player answers through free-form dialogue and can take strategic actions.

**Step 6 — Investigation and Adaptation**

The AI analyzes statements, remembers claims, compares evidence, identifies contradictions, and adjusts questioning strategies.

Evidence can be revealed or verified during the investigation.

**Step 7 — Final Verdict**

The interrogation concludes with an outcome determined by the player's defenses and the investigation findings.

**Step 8 — Cinematic Closing**

The detective delivers a personalized, sarcastic monologue.

**Step 9 — Case Breakdown**

The player receives the exact suspicion score, performance rating, contradictions, successful defenses, and missed opportunities.

**Step 10 — Progression**

The player receives applicable XP and unlock rewards, then chooses another case, replays a variation, or participates in a daily challenge.

---

# 4. AI Detective — Intelligence Requirements

The detective must be a genuinely stateful, context-aware investigation system.

It must not simply pass the latest user message into a generic detective prompt.

## 4.1 Persistent Memory

The system must remember relevant player statements across interrogation turns.

Memory should track:

- Factual claims.
- Alibis.
- Locations.
- Times and timelines.
- Relationships.
- Explanations.
- Changes in statements.
- Resolved and unresolved contradictions.

## 4.2 Contradiction Detection

The system must recognize inconsistencies between:

- Different player statements.
- Player claims and established evidence.
- Claimed timelines.
- Witness statements and player explanations.

A potential contradiction must not automatically be considered proven.

Ambiguities, missing context, and alternative interpretations must be evaluated.

## 4.3 Evidence Reasoning

The detective must distinguish between:

- Established evidence.
- Player-reported claims.
- Witness allegations.
- Reasonable inferences.
- Unverified assumptions.

Only established case facts can be presented as verified evidence.

## 4.4 Strategic Interrogation

The detective should be capable of:

- Choosing relevant follow-up questions.
- Pursuing suspicious leads.
- Changing its interrogation approach.
- Strategically withholding evidence.
- Building multi-turn questioning strategies.
- Revisiting earlier statements.
- Responding to convincing explanations.
- Recognizing when a line of questioning is unproductive.

It should sometimes remember a suspicious statement and challenge it later instead of immediately exposing every inconsistency.

## 4.5 Adaptive Personality

The detective's communication style must reflect:

- Its individual personality.
- The player's responses.
- The current interrogation context.
- The difficulty level.
- The strength of the investigation.

Personality influences expression and tactics, not factual accuracy.

## 4.6 Fair Reasoning

The AI must:

- Avoid fabricated evidence.
- Avoid unsupported accusations presented as facts.
- Consider credible alternative explanations.
- Recognize resolved contradictions.
- Distinguish weak evidence from strong evidence.
- Avoid punishing a player merely for using creative explanations.
- Support outcomes that genuinely depend on player performance.

## 4.7 Separation of Intelligence and Rules

Conceptually, the architecture should separate:

**Investigator**

Analyzes evidence, claims, timelines, and contradictions.

**Detective**

Plans interrogation tactics and produces natural dialogue.

**Referee / Game Engine**

Evaluates validated investigation findings and applies scoring and verdict rules.

These represent responsibilities, not a requirement for three independent LLM agents.

The specific orchestration approach will be selected during Phase 2.

---

# 5. Game Rules and Verdict Principles

## 5.1 Canonical Case Truth

Every case variation has an established set of facts and hidden information.

These facts remain consistent throughout the interrogation.

Player-generated statements do not automatically rewrite canonical evidence.

## 5.2 Player Influence

The interrogation outcome must be meaningfully influenced by the player's responses.

A strong explanation can weaken the importance of suspicious evidence.

An unsupported or contradictory statement can strengthen the detective's case.

## 5.3 Suspicion Is Not the Sole Verdict Rule

Suspicion reflects the current investigative assessment.

It must not independently determine every win or loss.

The final verdict considers evidence, successful defenses, contradictions, and other relevant factors under consistent rules.

## 5.4 Persuasion Must Be Grounded

Persuasion is not simply an LLM deciding that an answer sounds confident.

The game should consider whether the player's explanation is:

- Relevant.
- Internally consistent.
- Compatible with known facts.
- Reasonably supported.
- Responsive to the detective's challenge.

The precise scoring formula remains a Phase 2 design task.

## 5.5 Player Victory and Defeat

Guilty players succeed when they avoid being convincingly implicated under the game's verdict rules.

Innocent players succeed when they establish a sufficiently credible defense against the accusation.

Both roles must support meaningful success and failure states.

The detective must be capable of losing.

---

# 6. Mobile Application Requirements

The MVP must provide a complete mobile game experience.

## 6.1 Essential Screens

- Welcome and onboarding.
- Authentication.
- Home dashboard.
- Case selection and details.
- Cinematic introduction.
- Case briefing.
- Interrogation interface.
- Evidence viewer.
- Final verdict and cinematic monologue.
- Detailed case breakdown.
- Player profile.
- XP and progression.
- Detective selection and unlocks.
- Daily challenges.
- Store and purchases.
- Settings.

## 6.2 Authentication and Profiles

The product requires user authentication and persistent profiles.

Profiles should retain game progress, earned XP, rank, unlocks, and relevant purchases.

The exact authentication providers and guest-account policy will be finalized during technical design.

## 6.3 Mobile Gameplay Experience

The interface should emphasize the detective conversation, tension, story, evidence, and player responses.

The suspicion meter must remain qualitative during interrogation.

The complete numerical scoring breakdown is displayed only after the verdict.

## 6.4 Session Recovery

Unfinished sessions must resume without losing investigation state or contextual memory.

---

# 7. Progression and Retention

The progression system should encourage players to return without making gameplay feel like repetitive grinding.

Primary retention features:

- New cases and variations.
- Multiple detective personalities.
- Difficulty progression.
- XP and ranks.
- Unlockable detectives.
- Achievements.
- Daily Case Challenge.
- Daily streaks.
- Replayable investigations.
- Shareable results.

Players should feel that they are improving their ability to outsmart detectives.

---

# 8. Monetization Requirements

## 8.1 Free Experience

The free experience should give players a genuine opportunity to enjoy Alibi.

Free users can access starter cases and daily gameplay subject to clearly disclosed limits.

## 8.2 Premium Content

Players can purchase optional themed case collections.

Ownership of a case collection should be distinguishable from the allowance for AI-powered interrogation sessions.

## 8.3 Interrogation Credits

Players can optionally purchase additional session credits.

The game should not charge for every message during an active interrogation.

Usage limits and payment rules must be communicated clearly.

## 8.4 Future Monetization

Potential future additions include:

- Premium detective content.
- Cosmetic character customizations.
- Rewarded advertisements.
- VIP subscriptions.

These are not required launch commitments.

## 8.5 AI Cost Control

Because interrogations consume AI inference resources, the system must be designed to measure and control usage costs.

Exact free allowances, credit quantities, session pricing, and case-pack pricing must be determined after AI cost benchmarking.

---

# 9. MVP Scope

## 9.1 In Scope

- Five handcrafted cases and validated variations.
- Guilty and innocent player scenarios.
- Three supported case categories.
- Two detective personalities.
- Stateful adaptive AI interrogation.
- Structured claim tracking and contradiction detection.
- Case evidence analysis.
- Player evidence interactions.
- Dynamic verdicts and suspicion.
- Cinematic story introductions.
- Personalized sarcastic verdict monologues.
- Detailed result breakdowns.
- Player authentication and profiles.
- Automatic save and resume.
- XP, ranks, achievements, and unlockable content.
- Daily Case Challenge.
- Freemium case access and optional session credits.
- Mobile gameplay application.

## 9.2 Out of Scope for the Initial Release

- Real-time multiplayer interrogation.
- Full independent investigation simulation.
- Unlimited autonomous AI-generated case creation.
- Large catalogs of detectives.
- Ten or more handcrafted cases at launch.
- Weekly competitive tournaments.
- Voice-based interrogation as a required feature.
- Mandatory subscriptions.
- Pay-per-message monetization.
- Multiple simultaneous active investigation saves.

These may be reconsidered after launch based on player feedback and retention.

---

# 10. Quality and Acceptance Criteria

The initial product must satisfy the following requirements.

## AI Intelligence

- The detective can accurately reference important statements made earlier in an interrogation.
- It identifies genuine contradictions without assuming every ambiguity is a lie.
- It does not introduce evidence absent from the current case variation.
- It adjusts questioning based on player responses.
- It can strategically revisit previous statements.
- It responds appropriately when players challenge its reasoning.
- Its verdict is supported by the actual interrogation.

## Gameplay

- Players can complete a case from introduction to final verdict.
- Player decisions can produce different justified outcomes.
- The guilty and innocent roles have meaningful objectives.
- Difficulty levels provide distinguishable interrogation experiences.
- Players can inspect and request permitted evidence.
- Case variations remain logically consistent.

## Detective Personalities

- Both launch detectives have recognizable personalities.
- Their interrogation styles differ meaningfully.
- Both maintain reliable memory and reasoning.
- Their cinematic monologues reflect their personality and the actual game outcome.

## Mobile Application

- Players can create or access an account through the finalized authentication flow.
- Player progression persists.
- Unfinished interrogations can be resumed.
- Suspicion levels update during gameplay.
- The exact score is revealed at the verdict.
- Results, unlocks, and daily challenges are accessible from the mobile interface.

## Monetization

- Players can complete the supported free experience.
- Paid content and additional session credits can be purchased through the selected payment integration.
- Users are not charged per individual message.
- Usage limits are enforced consistently.
- Payments and entitlements persist correctly.

---

# 11. Items Intentionally Left Open

The following were not finalized during the 20 Phase 1 decisions and must not be treated as confirmed requirements.

**Product and Content**

- Names, appearances, and biographies of the two detectives.
- Final five case titles and individual storylines.
- Number and distribution of case variations.
- Exact balance of guilty and innocent cases.
- Exact rank names and XP rewards.
- Achievement catalog and unlock thresholds.
- Final scoring formulas and suspicion thresholds.
- Precise evidence interaction limits.

**Technical Architecture**

- Final LLM provider and model selection.
- Agent orchestration implementation and number of model calls.
- Final database schema.
- Authentication provider and guest-account approach.
- API contracts and deployment infrastructure.
- AI evaluation datasets and performance targets.

**Business and Operations**

- Premium case-pack pricing.
- Free interrogation allowances.
- Credit quantities and pricing.
- AI cost budget per interrogation.
- Final payment integration.
- Launch date and release regions.

---

# 12. Development Strategy

Alibi will follow the agreed 14-phase development roadmap.

1. Product Requirements and Game Design.
2. System Architecture.
3. Backend Foundation.
4. Authentication and Users.
5. Case Management.
6. Core Game Engine.
7. AI Memory System.
8. AI Investigation Engine.
9. Intelligent Detective Agent.
10. Referee and Scoring.
11. Mobile Application.
12. Engagement and Monetization.
13. Testing and Optimization.
14. Deployment and Launch.

These are development workstreams. Some work should happen in parallel, particularly mobile UI development and ongoing AI evaluation.

**First engineering milestone:** Deliver one complete playable case with reliable interrogation, persistent memory, justified verdicts, and a usable mobile interface.

Expand to the full five-case Balanced MVP after validating the foundational experience.

---

# 13. Product Success Criteria

The product should be evaluated on both gameplay quality and AI intelligence.

**Gameplay metrics**

- Case start-to-completion rate.
- Percentage of players starting another case.
- Case replay rate.
- Daily challenge participation.
- Player retention.
- Progression and unlock engagement.

**AI quality metrics**

- Claim memory accuracy.
- Contradiction identification accuracy.
- Rate of unsupported evidence claims.
- Quality of adaptive follow-up questions.
- Verdict consistency and fairness.
- Interrogation latency and cost.

**Business metrics**

- Free-to-paid conversion.
- Case-pack purchases.
- Credit purchases.
- AI cost per completed interrogation.
- Revenue relative to AI and infrastructure costs.

The most important early validation question is:

**Do players enjoy trying to outsmart the AI detective enough to voluntarily start another interrogation?**

---

# 14. Final Product Statement

Alibi is a story-driven mobile interrogation game centered on intelligent AI detectives, psychological strategy, persuasion, and deception.

Players enter fictional investigations as guilty or innocent suspects, construct their defenses through natural conversation, and face detectives that remember, reason, challenge, and adapt.

Every interrogation should feel personal, unpredictable, and grounded in consistent case facts.

The game's defining experience is not simply talking to an AI character.

**It is trying to outsmart an intelligent opponent who remembers what you said, notices what you hide, and isn't afraid to make fun of you when your story falls apart.**

And when the player wins, the detective should be just cocky enough to make that victory feel even better.

---

**End of PRD — Version 1.0**  
**Phase 1: Complete**  
**Next Phase: System Architecture**
