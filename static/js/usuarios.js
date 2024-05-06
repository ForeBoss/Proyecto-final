$(document).ready(function(){
	$('#guardar_usuario').click(function(){
		$('#userModal').modal({
			backdrop: 'static',
			keyboard: false
		});
		$("#userModal").on("shown.bs.modal", function () {
			$('#userForm')[0].reset();
			$('.modal-title').html("<i class='fa fa-plus'></i> Agregar Usuario");
			$('#action').val('addUser');
			$('#save').val('Guardar');
		});
	});
});
