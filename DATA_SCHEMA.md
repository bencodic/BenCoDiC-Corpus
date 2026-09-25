# BenCoDiC Data Schema

This document describes the released BenCoDiC corpus schema and its relationship to the conceptual star schema presented in the manuscript.

## 1. Schema Overview

BenCoDiC contains 50,250 textual instances representing YouTube video captions, comments, and replies. The conceptual model consists of the `CyberbullyingAnalysis` fact table and nine analytical dimensions: `User`, `Video`, `TextualContent`, `Context`, `Time`, `ImpactScore`, `PoliticalParty`, `TargetIdentity`, and `Language`.

The released corpus is provided as a single flattened table in which each row represents one textual instance.

## 2. Released Column Order

The corpus contains 24 columns in the following order:

```text
slno
userId
handler
title
subscriberCount
videoCount
userViewCount
joinedDate
contentId
contentType
partyName
partyShortName
duration
viewCount
commentCount
text
publishedTime
likeCount
replyCount
parentSlno
grandparentSlno
targetName
languageName
bullyLabel
```

## 3. Column Dictionary

| Column | Schema Component | Type / Format | Description |
|---|---|---|---|
| `userId` | User | String | Identifier of the YouTube channel associated with the textual instance. User-generated channel identifiers are anonymized. |
| `handler` | User | String | Channel handle associated with `userId`. User-generated handles are anonymized. |
| `title` | User | String | Channel title associated with `userId`. User-generated channel titles are anonymized. |
| `subscriberCount` | User | Integer | Subscriber count recorded at data collection time. |
| `videoCount` | User | Integer | Number of videos uploaded by the associated channel at data collection time. |
| `userViewCount` | User | Integer | Total channel view count at data collection time. |
| `joinedDate` | User | String (`YYYY-MM-DD`) | Date on which the associated channel joined YouTube. |
| `duration` | Video | String (ISO 8601 duration) | Duration of the source video. |
| `viewCount` | Video | Integer | Source-video view count at data collection time. |
| `commentCount` | Video | Integer | Source-video comment count at data collection time. |
| `slno` | TextualContent | Integer | Unique serial number used to identify each instance and reconstruct the conversational hierarchy. |
| `contentId` | TextualContent | String | Source video ID for a caption, or YouTube comment/reply ID for a comment or reply. |
| `contentType` | TextualContent | String (categorical) | `caption`, `comment`, or `reply`. |
| `text` | TextualContent | String | Text of the caption, comment, or reply. |
| `parentSlno` | Context | Integer | Serial number of the direct parent in the hierarchy. |
| `grandparentSlno` | Context | Integer | Serial number of the associated source caption. |
| `publishedTime` | Time | String (ISO 8601 datetime) | Publication date and time of the video, comment, or reply. |
| `likeCount` | Video / ImpactScore | Integer | Source-video likes for captions, and textual-instance likes for comments/replies. |
| `replyCount` | ImpactScore | Integer | Number of replies to a top-level comment. |
| `partyName` | PoliticalParty | String (categorical) | Full political-party category associated with the source video. |
| `partyShortName` | PoliticalParty | String (categorical) | Abbreviated political-party category associated with the source video. |
| `targetName` | TargetIdentity | String (categorical) | Target-identity category assigned to the textual instance. |
| `languageName` | Language | String (categorical) | Language category assigned to the textual instance. |
| `bullyLabel` | CyberbullyingAnalysis (Fact) | String (categorical) | Gold-standard binary label: `bully` or `not bully`. |

## 4. Conversational Hierarchy

| `contentType` | `parentSlno` | `grandparentSlno` |
|---|---|---|
| `caption` | Own `slno` | Own `slno` |
| `comment` | Source caption `slno` | Source caption `slno` |
| `reply` | Parent comment `slno` | Source caption `slno` |

This structure allows the parent comment and source caption of a reply to be recovered directly.

## 5. Allowed Categorical Values

| Field | Values |
|---|---|
| `contentType` | `caption`, `comment`, `reply` |
| `partyShortName` | `AL`, `BNP`, `JaPa`, `Jamaat`, `NCP`, `Other` |
| `targetName` | `male`, `female`, `individual`, `people group`, `organization`, `general people` |
| `languageName` | `bengali`, `romanized bengali`, `code-mix`, `english`, `emoji-only` |
| `bullyLabel` | `bully`, `not bully` |

Political-party, target-identity, and language labeling procedures are described in `DATA_EXTRACTION.md`. Cyberbullying annotation is described in `ANNOTATION_GUIDELINES.md`.

## 6. Content-Type-Specific Metadata

| Field | Caption | Comment | Reply |
|---|---|---|---|
| `duration` | Source-video duration | Not applicable | Not applicable |
| `viewCount` | Source-video views | Not applicable | Not applicable |
| `commentCount` | Source-video comment count | Not applicable | Not applicable |
| `partyName` | Source-video party category | Recoverable through source caption | Recoverable through source caption |
| `partyShortName` | Source-video party abbreviation | Recoverable through source caption | Recoverable through source caption |
| `likeCount` | Source-video likes | Comment likes | Reply likes |
| `replyCount` | Not applicable | Number of replies | Not applicable |

## 7. User Anonymization

To protect user privacy, `userId`, `handler`, and `title` are anonymized for commenters and repliers. Caption rows retain public source-news-channel information. Channel-level numerical metadata are retained.

## 8. Relationship to the Conceptual Star Schema

The manuscript presents separate identifiers such as `videoId`, `contextId`, `timeId`, `impactScoreId`, `partyId`, `languageId`, and `targetId`. Because the released corpus is flattened, these surrogate identifiers are not stored as separate columns. Their attributes are stored directly in each record. The source YouTube video ID is represented by `contentId` on caption rows and is also provided in `video_list.csv`.
