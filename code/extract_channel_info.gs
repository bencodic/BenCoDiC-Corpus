function extractChannelInfo() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sourceSheet = ss.getSheets()[0];

  // Replace with your YouTube Data API key.
  var apiKey = 'YOUR_YOUTUBE_API_KEY';

  // The first column of the source sheet should contain YouTube channel handles.
  // Adjust the row range as needed.
  var startRow = 1;
  var endRow = 50;

  var result = [[
    'userId',
    'handler',
    'title',
    'subscriberCount',
    'videoCount',
    'userViewCount',
    'joinedDate'
  ]];

  const columnCount = result[0].length;
  var invalidHandleCount = 0;

  for (var row = startRow; row <= endRow; row++) {
    var authorDisplayName = String(
      sourceSheet.getRange(row, 1).getValue()
    ).trim();

    var authorChannelId = '';
    var channelTitle = '';
    var channelJoinDate = '';
    var subscriberCount = '';
    var videoCount = '';
    var viewCount = '';

    authorChannelId = getChannelIdByHandle(authorDisplayName);

    if (authorChannelId != '') {
      [channelTitle, channelJoinDate] = getChannelPrimaryInfo(authorChannelId, apiKey);

      [subscriberCount, videoCount, viewCount] = getChannelStatistics(authorChannelId, apiKey);
    } else {
      invalidHandleCount++;
    }

    result.push([
      authorChannelId,
      authorDisplayName,
      channelTitle,
      subscriberCount,
      videoCount,
      viewCount,
      channelJoinDate
    ]);
  }

  Logger.log(
    'Number of invalid channel handles: ' + invalidHandleCount
  );

  var newSheet = ss.insertSheet(ss.getNumSheets());

  newSheet.getRange(1, 1, result.length, columnCount).setValues(result);
}


// Extract the YouTube channel ID from a channel handle.
// Requires the Parser library used in the original extraction workflow.
// Apps Script Library ID: 1Mc8BthYthXx6CoIz90-JiSzSafVnT6U3t0z_W3hLTAX5ek4w0G_EIrNw
function getChannelIdByHandle(handle) {
  var url = 'https://www.youtube.com/' + handle;

  try {
    var html = UrlFetchApp.fetch(url).getContentText();

    var channelId = Parser
      .data(html)
      .from('<meta itemprop="identifier" content="')
      .to('"><span')
      .build()
      .trim();

    return channelId;

  } catch (e) {
    return '';
  }
}


// Extract channel title and channel creation date.
function getChannelPrimaryInfo(channelId, apiKey) {
  var url =
    'https://www.googleapis.com/youtube/v3/channels' +
    '?part=snippet&id=' +
    channelId +
    '&key=' +
    apiKey;

  var response = UrlFetchApp.fetch(url);
  var json = JSON.parse(response.getContentText());
  var channelInfo = json.items[0].snippet;

  return [
    channelInfo.title,
    channelInfo.publishedAt
  ];
}


// Extract channel subscriber count, video count, and view count.
function getChannelStatistics(channelId, apiKey) {
  var url =
    'https://www.googleapis.com/youtube/v3/channels' +
    '?part=statistics&id=' +
    channelId +
    '&key=' +
    apiKey;

  var response = UrlFetchApp.fetch(url);
  var json = JSON.parse(response.getContentText());
  var channelStat = json.items[0].statistics;

  return [
    channelStat.subscriberCount || '',
    channelStat.videoCount || '',
    channelStat.viewCount || ''
  ];
}
