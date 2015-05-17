function getCookie(name) {
   if (!name) { return null; }
    return decodeURIComponent(document.cookie.replace(new RegExp("(?:(?:^|.*;)\\s*" + encodeURIComponent(name).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=\\s*([^;]*).*$)|^.*$"), "$1")) || null; 
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
            if (user === null) {
              $.ajax({
                type: 'POST',
                url: '/user/login',
                data: {assertion: assertion},
                headers: {
                  "X-XSRFToken": getCookie("_xsrf")
                },
                success: function(res, status, xhr){
                  localStorage['email'] = res.email;
                  location.href = decodeURIComponent(window.location.search.substring(6));
                },
                error: function(xhr, status, err) {
                  localStorage['login_error'] = err;
                  navigator.id.logout();
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
          url: '/user/logout', // This is a URL on your website.
          headers: {
            "X-XSRFToken": getCookie("_xsrf")
          },
          success: function(res, status, xhr) {
              localStorage.removeItem('email');
              if (localStorage['login_error']) {
                $('#msg').empty();
                $('#msg').text('Login failure: ' + localStorage['login_error']);
                localStorage.removeItem('login_error');
              } else {
                location.href = '/';
              }
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
