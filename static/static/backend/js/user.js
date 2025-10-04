$('body').on('click', '.changePassword', function (e) {
    e.preventDefault();
    var urlUpdate = $(this).data('update');
    var modal = $('#myModalChangPassword');
    modal.find(".modal-footer > button[name=btn-changePassword]").attr('data-link', urlUpdate);
    modal.modal('show');
});

$('body').on('click', '.editUser', function (e) {
    e.preventDefault();
    var urlGet = $(this).data('get');
    var urlUpdate = $(this).data('update');
    $('.form-group').find('span.messageErrors').remove();
    $.ajax({
        type: "get",
        url: urlGet,
        dataType: 'json',
        success: function (result) {
            if (result.status === 200) {
                if (result.data !== undefined) {
                    $.each(result.data, function (elementName, value) {
                        $('.' + elementName).val(value);
                    });
                }
            }
        }
    });
    var modal = $('#updateUser');
    modal.find(".modal-footer > button[name=btn-updateUser]").attr('data-link', urlUpdate);
    modal.modal('show');
});
$('body').on('click', '#btn-updateUser', function (e) {
    var url = $(this).data('link');
    var form =  $('form#data-form-updateUser');
    var valueForm = form.serialize();
    $('.form-group').find('span.messageErrors').remove();
    $("br").remove();

    $.ajax({
        type: 'PATCH',
        url: url,
        data: valueForm,
        dataType: 'json',
        success: function (result) {
            Swal.fire(
                'Success!',
                ``,
                'success'
            )
            var modal = $('#updateUser');
            $(modal).modal('hide');
            oTable.draw();
        },error: function (errors) {
            var response = errors.responseJSON;
            $.each(response.errors, function (elementName, arrMessagesEveryElement) {
                $.each(arrMessagesEveryElement, function (messageType, messageValue) {
                    $(form).find('.' + elementName).parents('.form-group').append('<span class="messageErrors" style="color:red">' + messageValue + '</span><br>');
                });
            });
            if(response.errors == null){
                Swal.fire(
                    'Error!',
                    ``,
                    'error'
                )
            }
        }
    });
});

$('body').on('click', '#btn-changePassword', function (e) {
    var url = $(this).data('link');
    var form =  $('form#data-form');
    var valueForm = form.serialize();
    $('.form-group').find('span.messageErrors').remove();
    $("br").remove();

    $.ajax({
        type: 'PATCH',
        url: url,
        data: valueForm,
        dataType: 'json',
        success: function (result) {
            Swal.fire(
                'Success!',
                ``,
                'success'
            )
            var modal = $('#myModal');
            $(modal).modal('hide');
        },error: function (errors) {
            var response = errors.responseJSON;
            $.each(response.errors, function (elementName, arrMessagesEveryElement) {
                $.each(arrMessagesEveryElement, function (messageType, messageValue) {
                    $(form).find('.' + elementName).parents('.form-group').append('<span class="messageErrors" style="color:red">' + messageValue + '</span><br>');
                });
            });
            if(response.errors == null){
                Swal.fire(
                    'Error!',
                    ``,
                    'error'
                )
            }
        }
    });
});
