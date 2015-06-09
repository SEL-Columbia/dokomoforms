function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

(function () {
    navigator.id.watch({
      loggedInUser: localStorage['email'] || null,
      onlogin: function(assertion) {
        $.ajax({
          type: 'GET',
          url: '',
          success: function (res, status, xhr) {
            var user = localStorage['email'] || null;
            if (user === null){
              $.ajax({
                type: 'POST',
                url: '/user/login/persona',
                data: {assertion:assertion},
                headers: {
                  "X-XSRFToken": getCookie("_xsrf")
                },
                success: function(res, status, xhr){
                  localStorage['email'] = res.email;
                  location.href = decodeURIComponent(window.location.search.substring(6));
                },
                error: function(xhr, status, err) {
                  navigator.id.logout();
                  alert("Login failure: " + err);
                }
              });
            }
          }
        });
      },
      onlogout: function() {
        // A user has logged out! Here you need to:
        // Tear down the user's session by redirecting the user or making a call to your backend.
        // Also, make sure loggedInUser will get set to null on the next page load.
        // (That's a literal JavaScript null. Not false, 0, or undefined. null.)
        $.ajax({
          type: 'POST',
          url: '/', // This is a URL on your website.
          headers: {
            "X-XSRFToken": getCookie("_xsrf")
          },
          success: function(res, status, xhr) {
              localStorage.removeItem('email');
              location.href = '/';
          },
          error: function(xhr, status, err) { alert("Logout failure: " + err); }
        });
      }

    });
    
    $('.btn-login').click(function(){
        navigator.id.request();
    });
    $('.btn-logout').click(function(){
        navigator.id.logout();
    });
})();
