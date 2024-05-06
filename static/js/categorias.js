$(document).ready(function(){	
	$('#guardar_categoria').click(function(){
		$('#categoryModal').modal({
			backdrop: 'static',
			keyboard: false
		});
		$("#categoryModal").on("shown.bs.modal", function () {
			$('#categoryForm')[0].reset();
			$('.modal-title').html("<i class='fa fa-plus'></i> Agregar Categoria");
			$('#action').val('guardar_categoria');
			$('#save').val('Guardar');
		});
	});
});
