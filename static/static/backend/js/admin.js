
$('body').on('click', '.editAdmin', function (e) {
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
    var modal = $('#updateAdmin');
    modal.find(".modal-footer > button[name=btn-updateAdmin]").attr('data-link', urlUpdate);
    modal.modal('show');
});
$('body').on('click', '#btn-updateAdmin', function (e) {
    var url = $(this).data('link');
    var form =  $('form#data-form-updateAdmin');
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
            var modal = $('#updateAdmin');
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

$('#modalChangePasswordAdmin').on('hidden.bs.modal', function (e) {
    // $('#myModal').find("input[type=text],input[type=number],input[type=hidden], select").val('').prop('disabled',false);
    $('#modalChangePasswordAdmin').find("input[type=text],input[type=number],input[type=hidden],input[type=file],input[type=password], select").val('');
    $('.form-group').find('span.messageErrors').remove();
    $("br").remove();

});

$('body').on('click', '.changePasswordAdmin', function (e) {
    e.preventDefault();
    var urlUpdate = $(this).data('update');
    var modal = $('#modalChangePasswordAdmin');
    modal.find(".modal-footer > button[name=btn-changePasswordAdmin]").attr('data-link', urlUpdate);
    modal.modal('show');
});


$('body').on('click', '#btn-changePasswordAdmin', function (e) {
    var url = $(this).data('link');
    var form =  $('form#data-form-changePasswordAdmin');
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
            var modal = $('#modalChangePasswordAdmin');
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
