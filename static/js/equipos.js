$(document).ready(function(){
    $('#guardar_equipo').click(function(){
        $('#equipoModal').modal({
            backdrop: 'static',
            keyboard: false
        });
        $("#equipoModal").on("shown.bs.modal", function () {
            $('#equipoForm')[0].reset();
            $('.modal-title').html("<i class='fa fa-plus'></i> Agregar/Editar Equipo");
            $('#action').val('guardar_equipo');
            $('#save').val('Guardar');
        });
    });
});

