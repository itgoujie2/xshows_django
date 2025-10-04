$(document).ready(function () {

$( ".toogle-a" ).click(function() {
  $( ".right-header" ).toggleClass('show');
  $(this).toggleClass('active');
})
$( ".category-m" ).click(function() {
  $( ".menu-left" ).toggleClass('show');
  $( ".bg-cate" ).toggleClass('show');
  $(this).toggleClass('active');
  $("body, html").toggleClass('hide');
})
$( ".bg-cate" ).click(function() {
  $( ".menu-left" ).removeClass('show');
  $( ".bg-cate" ).removeClass('show');
  $( ".category-m" ).removeClass('active');
  $("body, html").removeClass('hide');
})
var msnry = new Masonry( '.grid', {
  icolumnWidth: '.grid-sizer',
  itemSelector: '.grid-item',
  percentPosition: true
});

    var rightHeight = $('.main-content .grid').height();
    $('.menu-left ul').height(rightHeight + 135);
});

// Get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

$('body').on('click', 'div.favourite', function (e) {
    e.preventDefault();
    var element = $(this);
    var url = $(this).data('url');
    $.ajax({
        type: "POST",
        url: url,
        dataType: 'json',
        success: function (result) {
            if(element.find(".fav-model").hasClass('active')){
                element.find(".fav-model").removeClass('active');
            }else{
                element.find(".fav-model").addClass('active');
            }

            if(element.find(".detail-favorites").hasClass('active')){
                element.find(".detail-favorites").removeClass('active');
            }else{
                element.find(".detail-favorites").addClass('active');
            }

            alertify.success(result.msg);
        },error: function (errors) {
            var response = errors.responseJSON;
            if(response.errors == null){
                alertify.error(response.msg);
            }
        }
    });
});

// Subscribe/Unsubscribe functionality for nudity alerts
$('body').on('click', '.subscribe-model', function (e) {
    e.preventDefault();
    e.stopPropagation();
    var element = $(this);
    var url = element.data('url');
    var modelId = element.data('model-id');

    console.log('Subscribe clicked, URL:', url);

    $.ajax({
        type: "POST",
        url: url,
        dataType: 'json',
        success: function (result) {
            console.log('Subscribe response:', result);
            if(result.success){
                var bellIcon = element.find('i');
                if(result.is_subscribed){
                    element.addClass('active');
                    element.css('color', '#ffc107');
                    bellIcon.removeClass('far').addClass('fas');
                    console.log('Subscribed - icon should be solid');
                }else{
                    element.removeClass('active');
                    element.css('color', '#999');
                    bellIcon.removeClass('fas').addClass('far');
                    console.log('Unsubscribed - icon should be hollow');
                }
                alertify.success(result.message);
            }
        },
        error: function (errors) {
            console.error('Subscribe error:', errors);
            var response = errors.responseJSON;
            if(response && response.msg){
                alertify.error(response.msg);
            } else {
                alertify.error('Failed to update subscription. Please try again.');
            }
        }
    });
});

function updateData(href, method,valueForm, message, modal = 'div#myModal', form ='form#data-form' ) {
    $.ajax({
        type: method,
        url: href,
        data: valueForm,
        dataType: 'json',
        success: function (result) {
            alertify.success(result.message);
            oTable.draw();
        },error: function (errors) {
            var response = errors.responseJSON;
            if(response.errors == null){
                alertify.error(response.msg);
            }
        }
    });
}
