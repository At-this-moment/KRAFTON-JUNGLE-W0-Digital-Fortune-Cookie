$(document).ready(function () {
    // 아이디의 입력이 변동되는 경우, 아이디 중복확인 초기화
    $('#signupUsername').on('input', function() {
        resetUsername();
    });

    // 비밀번호의 입력이 변동되는 경우, 유효성 검사 진행
    $('#signupPassword').on('input', function() {
        $('#help-pw2').addClass('hidden');
        checkPassword($('#signupPassword').val());
        resetCPW();
        if($('#confirmPassword').val() != "") {
            checkConfirmedPassword($('#confirmPassword').val());
        }
    });

    // 비밀번호 재입력이 변동되는 경우, 동일성 검사 진행
    $('#confirmPassword').on('input', function() {
        checkConfirmedPassword($('#confirmPassword').val());
    });

    // 이름의 입력이 변동되는 경우, 유효성 검사 진행
    $('#signupName').on('input', function () {
        checkName($('#signupName').val());
    });

    $('#signupBirthdate').on('input', function () {
        $('#signupBirthdate').removeClass("border-red-500")
    });

    $('#signupGender').on('input', function () {
        $('#signupGender').removeClass("border-red-500")
    });
});

// 흔들리는 효과
function shake(object) {
    object.addClass('shake');
    setTimeout(function() {object.removeClass('shake');}, 500);
}

// 회원가입 취소하기
$(document).on("click", "#cancelSignup", function (e) {
    e.preventDefault();
    window.location = "/";
});

var isNotDuplicated = false; // 아이디 유효성 충족 및 중복확인 통과 여부 체크
var isValidPassword = false; // 비밀번호 유효성 충족 여부 체크
var isConfirmedPassword = false; // 비밀번호 재확인 통과 여부 체크
var isValidName = false; // 이름 유효성 충족 여부 체크

// 아이디 중복 확인하기
// DB 상에 이미 사용중인 ID가 있는지 확인합니다.
$(document).on("click", "#btn-check-dup", function (e) {
    e.preventDefault();
    checkDuplicated();
});

function checkDuplicated() {
    var username = $('#signupUsername').val();
    $('#help-id5').addClass('hidden');
    if(!username) {
        $('#signupUsername').addClass('border-red-500');
        $('#help-id2').removeClass('hidden');
        shake($('#fieldUsername'));
        return;
    } else {
        $('#signupUsername').removeClass('border-red-500');
        $('#help-id2').addClass('hidden');
    }
    
    // 유효성 검사도 동시에 진행
    const regex_id = /^[a-z0-9]{5,20}$/;
    if(!regex_id.test(username)) {
        $('#help-id1').addClass('text-red-600');
        $('#signupUsername').addClass('border-red-500');
        shake($('#fieldUsername'));
        return;
    } else {
        $('#help-id1').removeClass('text-red-600');
    }

    $.ajax({
        url: '/check_username',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: username
        }),
        success: function(res) {
			isNotDuplicated = true;
            $('#signupUsername').removeClass('border-red-500');
            $('#help-id3').removeClass('hidden');
            $('#help-id4').addClass('hidden');
        },
        error: function(res) {
            isNotDuplicated = false;
            $('#signupUsername').addClass('border-red-500');
            $('#help-id3').addClass('hidden');
            $('#help-id4').removeClass('hidden');
        }
    });
}

// 비밀번호 유효성 검사 함수
function checkPassword(password) {
    const regex_pw = /^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#$%^&*()_+={}\[\]:;"'<>,.?~`-]).{8,16}$/;
    if(!regex_pw.test(password)) {
        isValidPassword = false;
        $('#signupPassword').addClass('border-red-500');
        $('#help-pw1').addClass('text-red-600');
        $('#help-pw3').addClass('hidden');
    } else {
        isValidPassword = true;
        $('#signupPassword').removeClass('border-red-500');
        $('#help-pw1').removeClass('text-red-600');
        $('#help-pw3').removeClass('hidden');
    }
}

// 비밀번호 재확인 함수
function checkConfirmedPassword(cpw) {
    const pw = $('#signupPassword').val()
    if(pw == "") {
        isConfirmedPassword = false;
        $('#help-pw2').removeClass('hidden');
        shake($('#signupPassword'));
        $('#confirmPassword').val('');
    } else if(cpw != pw) {
        isConfirmedPassword = false;
        $('#help-pw2').addClass('hidden');
        $('#confirmPassword').addClass("border-red-500");
        $('#help-cpw2').removeClass("hidden");
        $('#help-cpw3').addClass("hidden");
    } else {
        isConfirmedPassword = true;
        $('#help-pw2').addClass('hidden');
        $('#confirmPassword').removeClass("border-red-500");
        $('#help-cpw2').addClass("hidden");
        $('#help-cpw3').removeClass("hidden");
    }
}

// 이름 유효성 검사 함수
function checkName(name) {
    const regex_name = /^[가-힣]+$/;
    if(!regex_name.test(name)) {
        isValidName = false;
        $('#signupName').addClass("border-red-500");
        $('#help-name2').removeClass("hidden");
    } else {
        isValidName = true;
        $('#signupName').removeClass("border-red-500");
        $('#help-name2').addClass("hidden");
    }
}

// 아이디 입력 필드 초기화
function resetUsername() {
    isNotDuplicated = false
    $('#signupUsername').removeClass('border-red-500');
    $('#help-id1').removeClass('text-red-600');
    $('#help-id2').addClass('hidden');
    $('#help-id3').addClass('hidden');
    $('#help-id4').addClass('hidden');
    $('#help-id5').addClass('hidden');
}

// 비밀번호 재입력 필드 초기화
function resetCPW() {
    isConfirmedPassword = false;
    $('#confirmPassword').removeClass('border-red-500');
    $('#help-cpw1').removeClass('text-red-600');
    $('#help-cpw2').addClass('hidden');
    $('#help-cpw3').addClass('hidden');
}

// 회원가입하기
$(document).on("click", "#submitSignup", function (e) {
    e.preventDefault();
    submitSignup();
});

function submitSignup() {
    // 체크사항을 하나라도 충족하지 못한 경우 회원가입 불가
    // 이름, 생년월일, 성별이 입력되지 않은 경우 회원가입 불가
    var username = $('#signupUsername').val();
    var password = $('#signupPassword').val();
	var password_confirm = $('#confirmPassword').val();
    var name = $('#signupName').val();
    var birthdate = $('#signupBirthdate').val();
    var gender = $('#signupGender').val();

    if(!isNotDuplicated || !isValidPassword || !isConfirmedPassword || !isValidName || username == "" || password == "" || password_confirm == "" || name == ""  || birthdate == "" || gender == "성별") {
        if(!isNotDuplicated || username == "") {
            shake($('#fieldUsername'));
            $('#signupUsername').addClass('border-red-500');
        }
        if(!isValidPassword || password == "") {
            shake($('#signupPassword'));
            $('#signupPassword').addClass('border-red-500');
        }
        if(!isConfirmedPassword || password_confirm == "") {
            shake($('#confirmPassword'));
            $('#confirmPassword').addClass('border-red-500');
        }
        if(!isValidName || name == "") {
            shake($('#signupName'));
            $('#signupName').addClass('border-red-500');
        }
        if(birthdate == "") {
            shake($('#signupBirthdate'));
            $('#signupBirthdate').addClass('border-red-500');
        }
        if(gender == "성별") {
            shake($('#signupGender'));
            $('#signupGender').addClass('border-red-500');
        }
        return;
    }

    $.ajax({
        url: '/signup',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            username: username,
            password: password,
			password_confirm: password_confirm,
            name: name,
            birthdate: birthdate,
            gender: gender
        }),
        success: function(res) {
            alert(res.msg);
			window.location = "/";
        },
        error: function(res) {
            alert(res.responseJSON.msg);
        }
    });
}