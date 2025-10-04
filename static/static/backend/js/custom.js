$('#perPage').change(function () {
    $('#form-filter').submit()
})
function loadingPage(display = true) {
    $('#pn-loading').css('display', display ? 'block' : 'none');
}
$('input[data-bootstrap-switch]').bootstrapSwitch()
var sortTable = {
    init: () => {
        $('#form-filter').append('<input type="hidden" name="sort_" id="input_sort" />');
        sortTable.submitSort();
    },
    submitSort: () => {
        $('.pn-sort').click(function () {
            $('#input_sort').attr('name', 'sort_' + $(this).data('fields'));
            $('#input_sort').val($(this).data('order'));
            $('#form-filter').submit();
        });
    }
};