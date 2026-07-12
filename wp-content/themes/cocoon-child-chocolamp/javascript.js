//ここに追加したいJavaScript、jQueryを記入してください。
//このJavaScriptファイルは、親テーマのJavaScriptファイルのあとに呼び出されます。
//JavaScriptやjQueryで親テーマのjavascript.jsに加えて関数を記入したい時に使用します。

(function () {
  document.addEventListener('DOMContentLoaded', function () {

    // ハンバーガーメニュー
    var hamburger = document.querySelector('.chocolamp-hamburger');
    var drawer = document.getElementById('chocolamp-drawer');
    var drawerClose = document.querySelector('.chocolamp-drawer-close');

    function openDrawer() {
      drawer.hidden = false;
      requestAnimationFrame(function () {
        drawer.classList.add('is-open');
      });
      hamburger.setAttribute('aria-expanded', 'true');
      document.body.classList.add('chocolamp-noscroll');
    }

    function closeDrawer() {
      drawer.classList.remove('is-open');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.classList.remove('chocolamp-noscroll');
      setTimeout(function () {
        drawer.hidden = true;
      }, 300);
    }

    if (hamburger && drawer) {
      hamburger.addEventListener('click', function () {
        if (drawer.classList.contains('is-open')) {
          closeDrawer();
        } else {
          openDrawer();
        }
      });
    }

    if (drawerClose) {
      drawerClose.addEventListener('click', closeDrawer);
    }

    if (drawer) {
      drawer.addEventListener('click', function (e) {
        if (e.target === drawer) closeDrawer();
      });
    }

    // サイト内検索パネル
    var searchToggle = document.querySelector('.chocolamp-search-toggle');
    var searchPanel = document.getElementById('chocolamp-search-panel');

    if (searchToggle && searchPanel) {
      searchToggle.addEventListener('click', function () {
        var isHidden = searchPanel.hidden;
        searchPanel.hidden = !isHidden;
        searchToggle.setAttribute('aria-expanded', String(isHidden));
        if (isHidden) {
          var input = searchPanel.querySelector('input[type="search"], input[type="text"]');
          if (input) input.focus();
        }
      });
    }

  });
})();
