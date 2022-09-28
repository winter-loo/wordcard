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
  console.log('post text: ', text);
  (async () => {
    const response = await fetch('http://pi.ldd.cool:1500/add', {
      method: 'POST',
      body: 'text=' + text,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    response.json().then(j => console.log(j));
  })();
}
