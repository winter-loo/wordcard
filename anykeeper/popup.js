var memoListEl = document.getElementById("memo-list");

(async () => {
    var li = document.createElement('li');
    li.setAttribute("id", "user-tip");
    li.textContent = "waiting...";
    memoListEl.appendChild(li); 
    const response = await fetch('http://ldd.cool:1500/memo/list', {
      method: 'GET',
    });
    response.json().then(j => ShowMemoList(j));
})();

function ShowMemoList(json_obj) {
    var userTipEl = document.getElementById('user-tip');
    memoListEl.removeChild(userTipEl);
    if (json_obj["error"] != 0) {
        var li = document.createElement('li');
        li.textContent = json_obj["error"];
        memoListEl.appendChild(li);
    } else {
        var memos = json_obj["data"];
        for (var i = 0; i < memos.length; i++) {
           var li = document.createElement('li');
           li.textContent = memos[i]['literal'];
           memoListEl.appendChild(li); 
        }
    }
}