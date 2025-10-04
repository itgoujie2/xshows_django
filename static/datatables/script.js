$('body').on('click', '.restore_data', function (e) {
    e.preventDefault();
    var href = $(this).data('link');
    alertify.confirm('Notification', 'Do you want to restore this data ?', function () {
            restore_data(href);
        }
        , function () {
        });
});


$('body').on('click', '.delete_data', function (e) {
    e.preventDefault();
    var href = $(this).data('link');
    alertify.confirm('Notification', 'Do you want to delete this data  ?', function () {
            delete_data(href);
        }
        , function () {
        });
})

$('body').on('change', '.status', function (e) {
    e.preventDefault();
    var href = $(this).attr('data-href');
    var value = $(this).val();
    alertify.confirm('Notification', 'Bạn có muốn thay đổi trạng thái dữ liệu này không ?', function () {
            updateStatus(href,value);
        }
        , function () {
        });
})

$('body').on('click', '.add_data', function (e) {
    e.preventDefault();
    var url = $(this).attr('data-href');
    $('.form-row').find('span.messageErrors').remove();
    $('#myModal').find(".modal-title").text('Add');
    $('#myModal').find(".modal-footer > button[name=btn-save]").html('Save');
    $('#myModal').find(".modal-footer > button[name=btn-save]").attr('data-link', url);
    $('#myModal').find(".modal-footer > button[name=btn-save]").attr('data-type', "add");
    $('#myModal').modal('show');
});

$('body').on('click', '.show_data', function (e) {
    e.preventDefault();
    var urlGet = $(this).attr('data-href-get');
    var urlUpdate = $(this).attr('data-href-update');
    var id = $(this).attr('data-id');
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
                        if(elementName.indexOf("image") !== -1 || elementName.indexOf("logo") !== -1 || elementName.indexOf("cover") !== -1 || elementName.indexOf("avatar") !== -1){
                            $("." + elementName).after('<img class="image-in-form '+ elementName+'-show" src="'+value+'" >');
                        }else if(elementName === "active") {
                            if(value == 1){
                                $('.' + elementName).prop('checked', true);
                            }else{
                                $('.' + elementName).prop('checked', false);
                            }
                        }else{
                                $('.' + elementName).val(value);
                        }
                    });
                }
            }
        }
    });
    $('#myModal').find(".modal-footer > button[name=btn-save]").html('Update');
    $('#myModal').find(".modal-footer > button[name=btn-save]").attr('data-link', urlUpdate);
    $('#myModal').find(".modal-footer > button[name=btn-save]").attr('data-type', "update");
    $('#myModal').modal('show');
});

$('body').on('click', '#btn-save', function (e) {
    var valueForm = $('form#data-form').serialize();
    var url = $(this).attr('data-link');
    var type = $(this).attr('data-type');
    $('.form-group').find('span.messageErrors').remove();
    $("br").remove();

    if(type === "update"){
        updateData(url, 'PUT', valueForm,'Updated successfully');
    }else{
        updateData(url, 'POST', valueForm,'Added successfully');
    }
});


$('#myModal').on('hidden.bs.modal', function (e) {
    // $('#myModal').find("input[type=text],input[type=number],input[type=hidden], select").val('').prop('disabled',false);
    $('#myModal').find("input[type=text],input[type=number],input[type=hidden],input[type=file],input[type=password], select").val('');
    $('.form-group').find('span.messageErrors').remove();
    $('#myModal').find('.image-in-form').remove();
    $("br").remove();

});

function updateData(href, method,valueForm, message, modal = 'div#myModal', form ='form#data-form' ) {
    $.ajax({
        type: method,
        url: href,
        data: valueForm,
        dataType: 'json',
        success: function (result) {
            alertify.success(message);
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
                alertify.error(response.msg);
            }
        }
    });
}

function updateDataWithFile(href, method,valueForm, message ) {
    valueForm.append("_method", method);
    $.ajax({
        type: 'POST',
        url: href,
        data: valueForm,
        processData: false,
        enctype: 'multipart/form-data',
        dataType: 'json',
        contentType: false,
        success: function (result) {
            alertify.success(message);
            $('div#myModal').modal('hide');
            oTable.draw();
        },error: function (errors) {
            var response = errors.responseJSON;
            $.each(response.errors, function (elementName, arrMessagesEveryElement) {
                $.each(arrMessagesEveryElement, function (messageType, messageValue) {
                    $('form#data-form').find('.' + elementName).parents('.form-group').append('<span class="messageErrors" style="color:red">' + messageValue + '</span><br>');
                });
            });
            if(response.errors == null){
                alertify.error(response.msg);
            }
        }
    });
}

function updateStatus(href, status) {
    $.ajax({
        type: 'PATCH',
        url: href,
        data: {
            "status" : status
        },
        dataType: 'json',
        success: function (data) {
            if (data.status === 200) {
                alertify.success('Updated successfully');
                oTable.draw();
            }
        }, error: function (data) {
            alertify.error(data.responseJSON.msg);
        }
    }).done(function (data) {

        $(this).prop('disabled', false);
    });
}

function restore_data(href) {
    $.ajax({
        type: 'PATCH',
        url: href,
        dataType: 'json',
        success: function (data) {
            if (data.status === 200) {
                alertify.success(data.msg);
                oTable.draw();
            }
        }, error: function (data) {
            alertify.error(data.responseJSON.msg);
        }
    }).done(function (data) {

        $(this).prop('disabled', false);
    });
}

function delete_data(href) {
    $.ajax({
        type: 'DELETE',
        url: href,
        dataType: 'json',
        success: function (data) {
            if (data.status === 200) {
                alertify.success(data.msg);
                oTable.draw();
            }
        }, error: function (data) {
            alertify.error(data.responseJSON.msg);
        }
    }).done(function (data) {

        $(this).prop('disabled', false);
    });
}


function dataTables(route, columns, id = '#data-datatables', orderCol = 0 ) {
    return $(id).DataTable({
        processing: true,
        serverSide: true,
        info: true,
        autoWidth: false,
        ajax: route,
        columns: columns,
        order: [[orderCol, "DESC"]],
        initComplete: function () {
            this.api().columns().every(function () {
                var column = this;
                var input = document.createElement("input");
                input.style.width = '100%';
                $(input).appendTo($(column.footer()).empty())
                    .on('change', function () {
                        var val = $.fn.dataTable.util.escapeRegex($(this).val());
                        column.search(val ? val : '', true, false).draw();
                    });
            });
        },
        language: {
            // "lengthMenu": "Hiển thị _MENU_ bản ghi mỗi trang",
            // "zeroRecords": "Không có bản ghi nào!",
            // "info": "Hiển thị trang _PAGE_ của tổng _PAGES_ trang",
            // "infoEmpty": "Không có bản ghi nào!!!",
            // "infoFiltered": "(Đã lọc từ tổng _MAX_ bản ghi)",
            // "paginate": {
            //     "previous": "Trang trước",
            //     "first": "Trang đầu",
            //     "next": "Trang sau",
            //     "last": "Trang cuối",
            // },
            processing: '<i class="fa fa-spinner fa-spin fa-1x fa-fw"></i><span class="sr-only">Loading...</span>'
        },
        pageLength: 10
    });
}

function showImage(className){
    $("."+className).change(function(e) {
        var imageShowName = className+"-show";
        $("."+imageShowName).remove();
        for (var i = 0; i < e.originalEvent.srcElement.files.length; i++) {
            var file = e.originalEvent.srcElement.files[i];
            var img = document.createElement("img");
            img.className = imageShowName;
            var reader = new FileReader();
            reader.onloadend = function() {
                img.src = reader.result;
            }
            reader.readAsDataURL(file);
            $("."+className).after(img);
            $("."+imageShowName).addClass('image-in-form');
        }
    });
}

var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
};
