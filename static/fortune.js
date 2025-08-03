$(document).ready(function() {
	var token = getCookie('access_token');
	if(!token || token == 'undefined') {
		alert("로그인 후 사용 가능합니다.");
		window.location = "/";
	}
});



$(document).on("click", "#open-cookie", function (e) {
    e.preventDefault();
	$("#open-cookie").prop("disabled", true);
    $.ajax({
        url: '/fortune',
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + getCookie('access_token') // localStorage.getItem('access_token')
        },
        success: function(res) {
			var messageArray = res.message.split('.');
			$("#text1").text(messageArray[0] + '.');
			$("#text2").text(messageArray[1] + '.');
			$("#text3").text(messageArray[2] + '.');
        },
        error: function(res) {
			console.log(res);
            alert(res.responseJSON.msg);
            window.location = "/";
        }
    });
	
    $('#open-cookie').addClass('fade');
    setTimeout(function() {
        $('#open-cookie').addClass('hidden');
        $('#dead-cookie').removeClass('hidden').addClass('fade-in').addClass('show');
		setTimeout(function() {
        $('#paper').removeClass('hidden').addClass('fade-in');
	        setTimeout(function() {
	            $('#paper').attr('src', "../static/paper2.png");
	            setTimeout(function() {
	                $('#text1').removeClass('hidden').addClass('fade-in');
	                setTimeout(function() {
	                    $('#paper').attr('src', "../static/paper3.png");
	                    setTimeout(function() {
	                        $('#text2').removeClass('hidden').addClass('fade-in');
	                        setTimeout(function() {
	                            $('#text3').removeClass('hidden').addClass('fade-in');
	                                setTimeout(function() {
	                                    $('#confirm-button').removeClass('hidden').addClass('fade-in');
	                                }, 250);
	                        }, 250);
	                    }, 250);
	                }, 500);
	            }, 250);
	        }, 500);
		}, 250);
    }, 500);
});

$(document).on("click", "#confirm-button", function (e) {
    e.preventDefault();
    window.location = "/";
});

function getCookie(name) {
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}