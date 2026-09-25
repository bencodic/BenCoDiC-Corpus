# BenCoDiC Annotation Guidelines

This document summarizes the context-aware guideline used to assign the binary labels `bully` and `not bully` in BenCoDiC.

## 1. Annotation Rule

Annotators evaluated each target text with its available conversational context. The seven categories below were used as annotation criteria, not as mutually exclusive class labels. A sample was labeled `bully` when at least one criterion was satisfied. Otherwise, it was labeled `not bully`. A sample could satisfy multiple criteria, with no precedence among them. Only the final binary label was retained.

## 2. Training and Context

The guideline was developed in consultation with a sociolinguistics expert, who conducted three one-hour training sessions on the guideline, contextual interpretation, and the distinction between `bully` and `not bully`.

Available context was used as follows:

- **Caption:** caption text
- **Comment:** caption and target comment
- **Reply:** caption, parent comment, and target reply

## 3. Annotation Criteria

### Cat1. Profanity or Slurs

Vulgar expressions, profane words, swearing, or slurs are labeled `bully`.

**Example:** কানকির পুত কি বলে  
**Translation:** What does the son of a prostitute say?

The word **কানকি** (prostitute) functions as a profane and derogatory expression.

### Cat2. Direct Personal Attack

Explicit threats, insults, demeaning expressions, or disparagement directed at an individual are labeled `bully`.

**Example:** তুই তো মীরজাফর  
**Translation:** You are a traitor.

### Cat3. Indirect Personal Attack

Implicit mocking, provocation, irritation, or disparagement of an individual without explicit abusive language is labeled `bully` when supported by context.

**Target text:** এত খিদা  
**Translation:** So much hunger.

**Caption:** জনপ্রতিনিধির হাতে ক্ষমতা হস্তান্তরের বিকল্প নেই: ফারুক  
**Translation:** There is no alternative to transferring power to the people's representatives: Faruk.

The target text appears harmless in isolation but functions as an indirect personal attack in context.

### Cat4. Direct Group or Organizational Attack

Explicit insults, demeaning expressions, dehumanization, or threats directed at a group or organization are labeled `bully`.

**Example:** এরা এখন হায়েনা হয়ে গেছে  
**Translation:** They have become cruel.

### Cat5. Indirect Group or Organizational Attack

Implicit mocking, provocation, irritation, or disparagement of a group or organization without explicit abusive language is labeled `bully` when supported by context.

**Target text:** জাতীয় পার্টির নতুন ভার্সন  
**Translation:** New version of the National Party.

**Caption:** রাষ্ট্রপতি ইস্যুতে নিজেদের অবস্থান স্পষ্ট করলো গণঅধিকার  
**Translation:** Gonadhikar clarified its position on the president issue.

The target text implicitly disparages the organization mentioned in the caption.

### Cat6. Support for Bullying Statements

A comment or reply that explicitly endorses a bullying statement is labeled `bully`.

**Comment:** এদের লজ্জা সরম বলতে কিছুই নেই  
**Translation:** They have no shame at all.

**Reply:** সহমত  
**Translation:** Agree.

The reply is labeled `bully` because it endorses the preceding bullying statement.

### Cat7. Insult through Negative Emojis

Derogatory emojis, such as shoe or dog emojis, are labeled `bully` when the target and surrounding context indicate an insult toward a person, group, or organization. Emoji presence alone is not sufficient.

## 4. Edge Cases

Neutral expressions, agreement replies, emojis, and sarcasm were interpreted using the available conversational context, as illustrated in Cat3, Cat5, Cat6, and Cat7. Romanized Bengali and Bengali-English code-mixed texts posed different linguistic challenges because of non-standard Romanized spelling and language mixing. These variations were considered during interpretation before applying the same seven annotation criteria.
