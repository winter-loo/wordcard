chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'chrome.ext.ldd.cool',
    title: 'keep: %s',
    contexts: ["selection"]
  });
});


chrome.contextMenus.onClicked.addListener((info, tab) => {
  console.log('menu item clicked: ', info);
  if (info.menuItemId == 'chrome.ext.ldd.cool') {
    postText(info.selectionText);
  }
});

const postText = text => {
  json_obj = { literal: text }
  console.log('post json: ', json_obj);
  (async () => {
    const response = await fetch('http://ldd.cool:1500/add', {
      method: 'POST',
      body: 'json=' + encodeURIComponent(JSON.stringify(json_obj)),
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    response.json().then(j => console.log(j));
  })();
}
