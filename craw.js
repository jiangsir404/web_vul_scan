var page = require('webpage').create();
page.onAlert = function (message) {
    console.log(message);
    return true;
};
page.onCallback = function() {
    page.evaluate(function(){
        atags = document.getElementsByTagName("a");
        for(var i=0;i<atags.length;i++){
            if (atags[i].getAttribute("href")){
                alert(atags[i].getAttribute("href"));
            }
        }
    })
    phantom.exit()
};
page.open("http://info.so.360.cn/about.html", "get", "", function (status) {
    page.evaluateAsync(function(){
        if (typeof window.callPhantom === 'function') {
            window.callPhantom();
        }
    }, 10000)
});