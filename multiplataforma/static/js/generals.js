$(document).ready(function() {
    $('.js-example-basic-single').select2();
     $('.table-normal').DataTable( {
		  scrollX: false,
		  responsive: true,
    });
     $('.table-no-pagin').DataTable( {
		  scrollX: false,
		  responsive: true,
		  paging: false
    });
     $('.table-no-order').DataTable( {
		  scrollX: false,
		  responsive: true,
		  ordering: false

    });


});

function register_staff(){

	$('.send-register').click(function(e){
		e.preventDefault()
		$('.modal-body').html("<p>Pronto no estaremos comunicando contigo por medio de correo para darte una respuesta</p")
		$('#Modal').modal()
		$('#Modal').removeClass('fade')
		$('#Modal').show()
		setTimeout(function() {
			$('.staff_register').submit()
		}, 2000);
	})


}


function check_username(){

$('#id_username').focusout(function(){
		username= $(this).val()
		$.get('/service/check-username/'+username, function( data ) {
		  if (data=="exits"){
		  	alert('Username ya existe')
			$('.username').addClass('red')
			$('#id_username').val('')
		  }else{
		  	 $('.username').removeClass('red')
		  }
		});
	});
}


function create_plan_subproduct(){
    $('body').on("click", ".delete" , function(event){
            event.preventDefault()
            var id = $(this).attr('id');
            var mensaje = confirm("Desea eliminar esta cuenta?");
            if (mensaje) {
                $.get('/delete/PlansPlatform/'+id ,function(data){
                    alert(data)
                    location.reload();
                })
            }
    });

     $('#add-marketplace').click(function(){

        var id = $(this).attr('id_package');
        $.get('/send-package-to-markeplace/'+id ,function(data){
                    alert(data)
                    location.href = "/platform/market-place";
        })
    })


    $('.create_plan').click(function(e){
        e.preventDefault()
        $(this).prop( "disabled", true );
        $('#create_plan_form').submit()
    })
}

function delete_saler(){
    $('#salers-table tbody').on("click", ".delete-user" , function(event){
        event.preventDefault()
        var id = $(this).attr('id');
        var mensaje = confirm("Desea desactivar este usuario?");
        if (mensaje) {
            $.get('/delete/User/'+id ,function(data){
                alert(data)
                location.reload();
            })
        }
    });
}

function buy_package(){

       $(function() {
          $('.starts').barrating({
            theme: 'fontawesome-stars',
            readonly: true
          });
       });


        $( ".sale" ).each(function() {
            $(this).on("click", function(event){
                event.preventDefault()
                var id = $(this).attr('id');
                name_product = $(this).attr('name_product')
                $('.modal-content').html('<div class="modal-header"><h2>¿Desea comprar '+name_product+'?</h2><button type="button" class="close" data-dismiss="modal"><i class="ti-close"></i></button></div><div class="modal-body"><button type="button" id="sale" class="btn btn-primary btn-md btn-block waves-effect text-center m-b-20">Aceptar</button></div>')
                $("#myModal").modal({show: true})
                $("#sale").on("click", function(event){
                    $(this).prop('disabled', true)
                    $.get('/package/buy/'+id ,function(data){
                        $('.modal-content').html(data)
                    })
                })
            });
        });

        $("#myModal").on("hidden.bs.modal", function () {
           location.reload();
        });

}

function sale_package(){

        $( ".sale" ).each(function() {
            $(this).on("click", function(event){
                event.preventDefault()
                var id = $(this).attr('id');
                name_product = $(this).attr('name_product')
                $.get('/package/sale-count/'+id ,function(data){
                        $('.modal-content').html(data)
                })
                $("#myModal").modal({show: true})


            });
        });

        $("#myModal").on("hidden.bs.modal", function () {
           location.reload();
        });

}




 function copiar(elemento){
    var $temp = $("<input>")
    $("body").append($temp);
    $temp.val($(elemento).text().replace("<br>","\n")).select();
    document.execCommand("copy");
    $temp.remove();
}

function set_pay_to_staff(){

    $('#pendding-table tbody').on("click", ".pay" , function(event){
        event.preventDefault()
        id = $(this).attr('id')
        $("#Modal").modal({show: true})
        $.get('/platform/sales/pay-staff-sale/'+ id ,function(data){
              $('.modal-content').html(data)

         })
    })

    $('body').on("click", "#pay" , function(event){
       location.reload();

    })

}


