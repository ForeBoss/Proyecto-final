$(document).ready(function(){
    $('#guardar_estudiante').click(function(){
        $('#studentModal').modal({
            backdrop: 'static',
            keyboard: false
        });
        $("#studentModal").on("shown.bs.modal", function () {
            $('#studentForm')[0].reset();
            $('.modal-title').html("<i class='fa fa-plus'></i> Agregar Estudiante");
            $('#action').val('guardar_estudiante');
            $('#save').val('Guardar');
        });
    });
});
