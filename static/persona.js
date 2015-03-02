function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

(function () {
    navigator.id.watch({
      loggedInUser: localStorage['email'] || null,
      onlogin: function(assertion) {
          console.log(window.location.href);
          console.log(window.location.host);
          console.log(document.URL);
        $.ajax({
          type: 'GET',
          url: '',
          success: function (res, status, xhr) {

            console.log("SUCCESS ONE");
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
                    console.log("SUCCESS TWO");
                  localStorage['email'] = res.email;
                  location.href = decodeURIComponent(window.location.search.substring(6));
                },
                error: function(xhr, status, err) {
                  navigator.id.logout();
                  alert("Login failure: " + err);
                }
              });
            }
          },
          error: function(xhr, status, err) {
              alert("Auth failure: " + err, xhr, status);
              console.log(xhr);
              console.log(status);
          }

        });
      },
      onlogout: function() {
        // A user has logged out! Here you need to:
        // Tear down the user's session by redirecting the user or making a call to your backend.
        // Also, make sure loggedInUser will get set to null on the next page load.
        // (That's a literal JavaScript null. Not false, 0, or undefined. null.)
        console.log("LOG OUT");
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
    
    $('#login').click(function(){
        navigator.id.request();
    });
    $('#logout').click(function(){
        navigator.id.logout();
    });
})();
