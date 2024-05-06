$(document).ready(function () {
    $('#registerLoan').click(function () {
        $('#registerLoanModal').modal({
            backdrop: 'static',
            keyboard: false
        });
        $("#registerLoanModal").on("shown.bs.modal", function () {
            $('#registerLoanForm')[0].reset();
            $('.modal-title').html("<i class='fa fa-plus'></i> Registrar Préstamo");
        });
    });
});
