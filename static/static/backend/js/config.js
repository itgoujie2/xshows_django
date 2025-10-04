$('body').on('click', '.edit-data', function (e) {
    e.preventDefault();
    var urlGet = $(this).data('get');
    var urlUpdate = $(this).data('update');
    var source = $(this).data('source');
    var id = $(this).data('id');

    var modal = $('#modal-'+source);
    $('.form-group').find('span.messageErrors').remove();
    $.ajax({
        type: "get",
        url: urlGet,
        data: {id: id},
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
    modal.find(".modal-footer > button[name=btn-save]").attr('data-link', urlUpdate);
    modal.find(".modal-footer > button[name=btn-save]").attr('data-source', source);
    modal.modal('show');
});

$('body').on('click', '#btn-save', function (e) {
    var url = $(this).data('link');
    var source = $(this).data('source');
    var form =  $('form#data-form-'+source);
    var valueForm = form.serialize();

    $('.form-group').find('span.messageErrors').remove();
    $("br").remove();

    $.ajax({
        type: 'PUT',
        url: url,
        data: valueForm,
        dataType: 'json',
        success: function (result) {
            Swal.fire(
                'Success!',
                ``,
                'success'
            )
            var modal = $('#modal-'+source);
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

$('.active-item').on('click', function (event, state) {
    var status = ( $(this).is(':checked') ) ? true : false;
    var id = $(this).data('id');
    var link = $(this).data('link');
    $.ajax({
        url: `${link}`,
        method: 'PATCH',
        dataType: 'JSON',
        data: {status: status === true ? 1 : 0},
        success: function (res) {
            if (res.status === 200) {
                Swal.fire(
                    'Success!',
                    ``,
                    'success'
                )
            } else {
                Swal.fire(
                    'Error!',
                    ``,
                    'error'
                )
                $(this).prop('checked', !event.target.checked);
            }
        },
        error: function (request) {
            Swal.fire(
                `${request.status}`,
                `${request.statusText}`,
                'error'
            );
        }
    })
})
