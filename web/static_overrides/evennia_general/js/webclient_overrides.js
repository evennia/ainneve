/* Stolen with <3 from evennia/web/webclient/static/webclient/js/webclient_gui.js */
// Handle text coming from the server
function onText(args, kwargs) {
    // append message to previous ones, then scroll so latest is at
    // the bottom. Send 'cls' kwarg to modify the output class.
    var renderto = "main";
    if (kwargs["type"] == "help") {
        if (("helppopup" in options) && (options["helppopup"])) {
            renderto = "#helpdialog";
        }
    }
    if (kwargs["type"] == "map") {
        if (("mappopup" in options) && (options["mappopup"])) {
            renderto = "#mapdialog";
        }
    }

    if (renderto == "main") {
        var mwin = $("#messagewindow");
        var cls = kwargs == null ? 'out' : kwargs['cls'];
        mwin.append("<div class='" + cls + "'>" + args[0] + "</div>");
        mwin.animate({
            scrollTop: document.getElementById("messagewindow").scrollHeight
        }, 0);

        onNewLine(args[0], null);
    } else {
        openPopup(renderto, args[0]);
    }
}
