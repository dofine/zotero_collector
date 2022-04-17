{
	"translatorID": "9444e3cb-e7d6-4735-b5f5-7d103838f3d9",
	"label": "xiaoyuzhou",
	"creator": "dofine",
	"target": "https?://www.xiaoyuzhoufm.com/episode/.*",
	"minVersion": "5.0",
	"maxVersion": "",
	"priority": 100,
	"inRepository": true,
	"translatorType": 4,
	"browserSupport": "gcsibv",
	"lastUpdated": "2022-04-10 15:23:58"
}

function detectWeb(doc, url) {
	return 'podcast';
}
function doWeb(doc, url) {
	const item = new Zotero.Item("podcast");
	const jsonld = doc.head.querySelector('script[name="schema:podcast-show"]').textContent;
	const data = JSON.parse(jsonld);

	const runningTimeExp = /PT(\d+)M/;
	// 时长
	const runningTime = runningTimeExp.exec(data.timeRequired)[1] + "min";
	item.runningTime = runningTime;
	if (data) {
		// 节目发布日期
		item.accessDate = ZU.strToISO(data.datePublished);
		item.seriesTitle = data.partOfSeries.name;
		// 暂时先把作者直接设定为播客名称，添加完毕之后可以手动修改
		item.creators = [{ lastName: data.partOfSeries.name, creatorType: "podcaster", fieldMode: 1 }]
		item.url = data.url;
		item.abstractNote = data.description;
	}
	const episodeTitle = doc.head.querySelector("meta[property='og:title']").content;
	item.title = episodeTitle;

	// 自动下载音频文件貌似行不通，暂时先不管了，先把音频文件链接写在 extra 里；
	const audioFile = doc.head.querySelector("meta[property='og:audio']").content;
	item.audioFile = audioFile;
	// item.attachments = [{
	// 	url:  audioFile,
	// 	title: episodeTitle,
	// 	mimeType: "audio/mpeg",
	// 	snapshot: false
	// }];
	const commentsText = doc.querySelectorAll('div.comment > div > div.text-wrap > div.text');  // 评论内容，不包括回复
	const commentsAuthor = doc.querySelectorAll('div.comment > div > div.info > div > div.name'); // 评论作者
	var comments = "<h1>热门评论</h1><ul>";
	if (commentsText.length >= 1) {
		for (var i = 0; i < 3; i++) {
			const commentContent = commentsAuthor[i].textContent + ": " + commentsText[i].textContent;
			comments = comments + "<li>" + commentContent + "</li>";

		}
	}
	item.notes.push({ note: comments + "</ul>" });
	item.complete();
}

/** BEGIN TEST CASES **/

/** END TEST CASES **/
