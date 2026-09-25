# BenCoDiC Data Extraction Procedure

This document describes source-video selection, YouTube data extraction, data integration, and auxiliary labeling for BenCoDiC.

## 1. Source Video Selection

The corpus was constructed from 100 political-news videos collected from eight Bengali YouTube news channels. Relevant videos were identified using party names, acronyms, and names of prominent associated leaders. The selected source videos were published from July 24 to November 10, 2024.

The exact source-video set is provided in `video_list.csv` with:

```text
videoId
userId
publishedDate
partyName
```

## 2. Extraction Workflow

Data extraction was implemented in Google Apps Script and divided into two stages to accommodate its execution-time limitation:

1. extraction of source-video records, comments, replies, and associated metadata
2. extraction of channel/user information

The resulting files were integrated using Python. The released scripts use an API-key placeholder and require a valid YouTube Data API key.

## 3. Stage 1: Text and Associated Metadata

The script `extract_text_and_metadata.gs` retrieves video information, top-level comments, replies, and associated metadata for each selected video.

### 3.1 Video Information

Three YouTube Data API v3 `videos` requests are used:

| Resource | `part` | Parameter | Retrieved information |
|---|---|---|---|
| `videos` | `snippet` | `id = videoId` | video title and publication time |
| `videos` | `contentDetails` | `id = videoId` | video duration |
| `videos` | `statistics` | `id = videoId` | view count, comment count, and like count |

The source-video record is stored with `contentType = caption`, and `snippet.title` is stored in `text`. The political-party category is specified at the source-video level according to the party represented directly in the video or through its associated leader or leaders.

### 3.2 Top-Level Comments

Top-level comments are retrieved using:

```text
YouTube.CommentThreads.list(
    'snippet',
    {
        videoId: <videoId>,
        maxResults: 100,
        pageToken: <nextPageToken>
    }
)
```

Pagination continues until no `nextPageToken` is returned. The script records the comment ID, author identifier, text, publication time, like count, and reply count.

### 3.3 Replies

Replies are retrieved using:

```text
YouTube.Comments.list(
    'snippet',
    {
        videoId: <videoId>,
        maxResults: 100,
        pageToken: <nextPageTokenRep>,
        parentId: <parentCommentId>
    }
)
```

Pagination continues until no further page token is returned. The script records the reply ID, author identifier, text, publication time, and like count.

`slno`, `parentSlno`, and `grandparentSlno` preserve the caption-comment-reply hierarchy defined in `DATA_SCHEMA.md`.

## 4. Stage 2: Channel/User Information

The script `extract_channel_info.gs` reads the Stage-1 `handler` values and resolves the corresponding YouTube channel IDs. Channel/user information is processed in configurable `startRow` and `endRow` ranges to accommodate the Google Apps Script execution-time limitation.

After a channel ID is resolved, two YouTube Data API v3 `channels` requests are used:

| Resource | `part` | Parameter | Retrieved information |
|---|---|---|---|
| `channels` | `snippet` | `id = channelId` | channel title and creation date |
| `channels` | `statistics` | `id = channelId` | subscriber count, video count, and total view count |

If a channel ID cannot be resolved, the corresponding channel-information fields remain empty.

## 5. Data Integration

The Stage-1 and Stage-2 spreadsheet outputs are combined in Python using the common `handler` field. The resulting data follow the structure defined in `DATA_SCHEMA.md`.

## 6. Auxiliary Labeling

Following integration, target identity and language category are added as auxiliary attributes.

### 6.1 Target Identity

Target identity is determined using a context-aware, rule-based procedure based on the textual content, available conversational context, and associated metadata.

### 6.2 Language Category

Language category is determined using a semi-automated procedure. Initial labels are generated through rule-based identification incorporating the Python `langdetect` module, followed by manual verification and correction where necessary.

The categorical values are defined in `DATA_SCHEMA.md`.
