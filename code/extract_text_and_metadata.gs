function extractTextAndMetadata() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // Read the YouTube video ID from cell A1 of the first sheet.
  var vid = ss.getSheets()[0].getRange(1, 1).getValue();

  // Replace the following placeholders before running the script.
  var apiKey = 'YOUR_YOUTUBE_API_KEY';
  var associatedParty = 'YOUR_PARTY_FULL_NAME';
  var partyShortName = 'YOUR_PARTY_SHORT_NAME';
  var channelHandler = 'YOUR_YOUTUBE_CHANNEL_HANDLER';

  channelHandler = channelHandler.toLowerCase();

  var result = [[
    'slno',
    'handler',
    'contentId',
    'contentType',
    'partyName',
    'partyShortName',
    'duration',
    'viewCount',
    'commentCount',
    'text',
    'publishedTime',
    'likeCount',
    'replyCount',
    'parentSlno',
    'grandparentSlno'
  ]];

  const columnCount = result[0].length;

  var nextPageToken = undefined;
  var slNo = 1;
  var captionSlNo = slNo;

  // Extract video caption and publication time.
  var [videoCaption, videoPublishedTime] =
    getVideoPrimaryInfo(vid, apiKey);

  // Extract video duration.
  var videoDuration =
    getVideoDuration(vid, apiKey);

  // Extract video-level statistics.
  var [videoViewCount, videoCommentCount, videoLikeCount] =
    getVideoStatistics(vid, apiKey);

  // Store the video caption.
  result.push([
    slNo,
    channelHandler,
    vid,
    'caption',
    associatedParty,
    partyShortName,
    videoDuration,
    videoViewCount,
    videoCommentCount,
    videoCaption,
    videoPublishedTime,
    videoLikeCount,
    '',
    captionSlNo,
    captionSlNo
  ]);

  // Extract comments.
  while (1) {

    var data = YouTube.CommentThreads.list(
      'snippet',
      {
        videoId: vid,
        maxResults: 100,
        pageToken: nextPageToken
      }
    );

    nextPageToken = data.nextPageToken;

    for (var row = 0; row < data.items.length; row++) {

      slNo++;

      var commentId = data.items[row].id;

      var authorDisplayName =
        data.items[row]
          .snippet
          .topLevelComment
          .snippet
          .authorDisplayName
          .toLowerCase();

      var commentSlNo = slNo;

      result.push([
        slNo,
        authorDisplayName,
        commentId,
        'comment',
        '',
        '',
        '',
        '',
        '',
        data.items[row].snippet.topLevelComment.snippet.textDisplay,
        data.items[row].snippet.topLevelComment.snippet.publishedAt,
        data.items[row].snippet.topLevelComment.snippet.likeCount,
        data.items[row].snippet.totalReplyCount,
        captionSlNo,
        captionSlNo
      ]);

      // Extract replies associated with the current comment.
      if (data.items[row].snippet.totalReplyCount > 0) {

        var parent =
          data.items[row].snippet.topLevelComment.id;

        var nextPageTokenRep = undefined;

        var replyParentId = commentSlNo;
        var replyGrandparentId = captionSlNo;

        while (1) {

          var data2 = YouTube.Comments.list(
            'snippet',
            {
              maxResults: 100,
              pageToken: nextPageTokenRep,
              parentId: parent
            }
          );

          nextPageTokenRep = data2.nextPageToken;

          for (var i = 0; i < data2.items.length; i++) {

            slNo++;

            var replyId = data2.items[i].id;

            var replyAuthorDisplayName =
              data2.items[i]
                .snippet
                .authorDisplayName
                .toLowerCase();

            result.push([
              slNo,
              replyAuthorDisplayName,
              replyId,
              'reply',
              '',
              '',
              '',
              '',
              '',
              data2.items[i].snippet.textDisplay,
              data2.items[i].snippet.publishedAt,
              data2.items[i].snippet.likeCount,
              '',
              replyParentId,
              replyGrandparentId
            ]);
          }

          if (
            nextPageTokenRep == "" ||
            typeof nextPageTokenRep === "undefined"
          ) {
            break;
          }
        }
      }
    }

    if (
      nextPageToken == "" ||
      typeof nextPageToken === "undefined"
    ) {
      break;
    }
  }

  // Store the extracted data in a new sheet.
  var newSheet = ss.insertSheet(ss.getNumSheets());

  newSheet
    .getRange(1, 1, result.length, columnCount)
    .setValues(result);
}


// Extract video caption and publication time.
function getVideoPrimaryInfo(vid, apiKey) {

  var url =
    'https://www.googleapis.com/youtube/v3/videos' +
    '?part=snippet&id=' +
    vid +
    '&key=' +
    apiKey;

  var response = UrlFetchApp.fetch(url);

  var json =
    JSON.parse(response.getContentText());

  var channelVideoInfo =
    json.items[0].snippet;

  return [
    channelVideoInfo.title,
    channelVideoInfo.publishedAt
  ];
}


// Extract video duration.
function getVideoDuration(vid, apiKey) {

  var url =
    'https://www.googleapis.com/youtube/v3/videos' +
    '?part=contentDetails&id=' +
    vid +
    '&key=' +
    apiKey;

  var response = UrlFetchApp.fetch(url);

  var json =
    JSON.parse(response.getContentText());

  return json.items[0].contentDetails.duration;
}


// Extract video view count, comment count, and like count.
function getVideoStatistics(vid, apiKey) {

  var url =
    'https://www.googleapis.com/youtube/v3/videos' +
    '?part=statistics&id=' +
    vid +
    '&key=' +
    apiKey;

  var response = UrlFetchApp.fetch(url);

  var json =
    JSON.parse(response.getContentText());

  var videoStat =
    json.items[0].statistics;

  return [
    videoStat.viewCount,
    videoStat.commentCount,
    videoStat.likeCount
  ];
}
