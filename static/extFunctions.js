/* global $ */

var watchIt = function watchIt (id, imgId, links, callback) {
    callback = callback || Function
    // To control change of select field and update image src whenever
    var toDo = function () {
        var idIndex = $(id + ' option:selected').val()
        $(imgId).attr('src', links[idIndex])
        callback(idIndex)
    }
    $(id).change(function () {
        toDo()
    })
    toDo()
}

var reloadIf = function (toGo, duration) {
    toGo = toGo || window.location.href
    duration = duration || 1000

    // To auto-reload the page if its served content has changed
    var storePage
    var location = window.location.href
    $.get(location, function(data) {
        storePage = data
    })
    setInterval(function () {
        $.get(location, function (data) {
           if (data !== storePage) window.location = toGo
        })
    }, duration)
}

var flashMsg = function (cate) {
    $('.postFlash').removeClass('hide')
    $('.postFlash > .alert-' + cate).removeClass('hide')
}

var announce = function (UserId,officeId) {
    // to $.get for repeating announcement and displaying flash message for success or failure
    var url = '/set_repeat_announcement/1';

    url+= '/' + UserId

    if (officeId !== undefined) url += '/' + officeId

    $.get(url, function (resp) {
        resp.status ? flashMsg('info') : flashMsg('danger')
    })
}


var copyToClipboard = function (text) {
    // copy `text` to clipboard
    var tempInput = document.createElement('input')

    tempInput.display = 'none;'
    tempInput.value = text

    document.body.appendChild(tempInput)
    tempInput.select()
    tempInput.setSelectionRange(0, 99999)
    document.execCommand('copy')
    document.body.removeChild(tempInput)
}


var updateUrlParamAndNavigate = function(param, value) {
    var url = new URL(location)
    var searchParams = new URLSearchParams(url.search)

    searchParams.set(param, value)

    url.search = searchParams.toString()
    window.location.href = url.toString()
}

function setupScrollMarquee($scrollContent) {
    if (!$scrollContent || !$scrollContent.length) return;

    var container = $scrollContent.closest('.scroll-container');
    if (!container.length) return;

    var contentEl = $scrollContent.get(0);
    

    // 1) If nothing inside, nothing to do
    if (!contentEl.children.length) {
        contentEl.style.animationDuration = '0s';
        return;
    }

    // 2) Build a clean HTML snapshot of current items
    var originalHTML = '';
    for (var i = 0; i < contentEl.children.length; i++) {
        originalHTML += contentEl.children[i].outerHTML;
    }

    // 3) Duplicate content for seamless loop: [A B C A B C]
    contentEl.innerHTML = originalHTML + originalHTML;

    // 4) Measure distance: we want to scroll through half of the duplicated width
    //    (that equals one full original sequence).
    var fullWidth = contentEl.scrollWidth;      // width of [A B C A B C]
    var distance = fullWidth / 2;               // pixels to move for one cycle

    // 5) Decide desired speed: pixels per second
    //    You can tweak this number to taste (slower/faster).
    var pixelsPerSecond = 240;                   // e.g. 80 px/s

    // 6) Duration in seconds = distance / speed
    var durationSeconds = distance / pixelsPerSecond;

    // 7) Apply animation duration
    contentEl.style.animationDuration = durationSeconds + 's';
}

