// 로그아웃
function logout() {
    alert("로그아웃되었습니다.");
    document.cookie = 'access_token' + '=; max-age=0; path=/';
    location.reload();
}

// 로그인 모달을 여는 함수
$(document).on("click", "#loginButton", function(e) {
    e.preventDefault;
    $("#loginModal").removeClass("hidden");
});

// 로그인 모달을 닫는 함수
$(document).on("click", "#closeModalFooter", function (e) {
    e.preventDefault();
    closeLoginModal();
});

function closeLoginModal() {
    $("#loginModal").addClass("hidden");
    $('#username').val('');
    $('#password').val('');
    $('#username').removeClass('border-red-500');
    $('#password').removeClass('border-red-500');
    $('#help-inputUsername').addClass('hidden');
    $('#help-inputPassword').addClass('hidden');
}

// 흔들리는 효과
function shake(object) {
    object.addClass('shake');
    setTimeout(function() {object.removeClass('shake');}, 500);
}

// 로그인 폼을 서버에 제출하는 함수
$(document).on("click", "#submitLogin", function (e) {
    e.preventDefault();
    var username = $('#username').val();
    var password = $('#password').val();
    // 아이디나 비밀번호가 입력되지 않은 경우 로그인 불가
    if (!username || !password) {
        if (!username) {
            $('#username').addClass('border-red-500');
            $('#help-inputUsername').removeClass('hidden');
            shake($("#username"));
        } else {
            $('#username').removeClass('border-red-500');
            $('#help-inputUsername').addClass('hidden');
        }
        if (!password) {
            $('#password').addClass('border-red-500');
            $('#help-inputPassword').removeClass('hidden');
            shake($("#password"));
        } else {
            $('#password').removeClass('border-red-500');
            $('#help-inputPassword').addClass('hidden');
        }
        return;
    }
    
    $.ajax({
        url: '/login',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: username,
            password: password
        }),
        success: function(res) {
            document.cookie = "access_token=" + res.access_token + "; path=/";
			// document.cookie = "access_token=" + res.access_token + "; path=/; max-age=" + 3600;
            location.reload();
        },
        error: function(res) {
            console.log(res);
            alert(res.responseJSON.msg);
        }
    });
});

// 회원가입 페이지로 이동하는 함수
$(document).on("click", "#signupButton", function(e) {
    e.preventDefault;
    window.location = "signup";
});

// 오늘의 쿠키 뽑기 페이지로 이동하는 함수
$(document).on("click", "#fcButton", function(e) {
    e.preventDefault;
    window.location = "fortune_page";
});