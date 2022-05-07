/* web socket with channels */
const MultiplataformaSocket = new WebSocket('ws://' + window.location.host+ '/marketplace/get-packages-socket' );

MultiplataformaSocket.onclose = function(e) {
    console.error('message socket closed unexpectedly');

};

function listenig_socket(){

	MultiplataformaSocket.onmessage = function(e) {
		var data = e.data;
		data_split = data.split('_')
		id = data_split[0]
		type = data_split[1]
		event = data_split[2]
		if (type =="False" && event == 'remove'){
            $('#card_'+id ).remove()
        }else if (type =="False" && event == 'hide'){
            $('.sale_'+id ).hide()
        }else if (type =="False" && event == 'show'){
            $('.sale_'+id ).show()
        }else if (type =="True" && event == 'reload'){
            location.reload();
        }


	};
}


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



    $('#id_password1').keyup(function(e) {
         var strongRegex = new RegExp("^(?=.{8,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$", "g");
         var mediumRegex = new RegExp("^(?=.{7,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$", "g");
         var enoughRegex = new RegExp("(?=.{6,}).*", "g");
         if (false == enoughRegex.test($(this).val())) {
                 $('#passstrength').html('Faltan caracteres.');
         } else if (strongRegex.test($(this).val())) {
                 $('#passstrength').className = 'ok';
                 $('#passstrength').html('Fuerte!');
         } else if (mediumRegex.test($(this).val())) {
                 $('#passstrength').className = 'alert';
                 $('#passstrength').html('Media!');
         } else {
                 $('#passstrength').className = 'error';
                 $('#passstrength').html('Débil!');
         }
         return true;
    });

     $(".staff_register").validate({
            rules: {
              id_address : {
                required: true,
                minlength: 10
              },
              id_document: {
                required: true,
                number: true,
                min: 10
              },
              id_phones: {
                required: true,
                min: 6
              },
               id_state: {
                required: true,
                min: 3
              },
               id_city: {
                required: true,
                min: 3
              },
               id_country: {
                required: true,
                min: 3
              },
               id_image: {
                required: true,
                min: 3
              },
               id_image_document: {
                required: true,
                min: 3
              },
              id_bank_info: {
                required: {
                  depends: function(elem) {
                    return $("#id_group").val() == "staff"
                  }
                }
              },
              id_first_name: {
                required: true,
                min: 6
              },
              id_last_name: {
                required: true,
                min: 6
              },
              id_email: {
                required: true,
                email: true
              },
              id_password1: {
                required: true,
                min: 8
              },
              id_password2: {
                required: true,
                equalTo:id_password1,
                min: 8
              },


            }
      });

	/*$('.send-register').click(function(e){

        e.preventDefault()
        $('.modal-body').html("<p>Pronto no estaremos comunicando contigo por medio de correo para darte una respuesta</p")
        $('#Modal').modal()
        $('#Modal').removeClass('fade')
        $('#Modal').show()
        setTimeout(function() {
            $('.staff_register').submit()
        }, 2000);
	})*/


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
                $.get('/delete/CountsPackage/'+id ,function(data){
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

function validate_form(){

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
                type_attr = $(this).attr('type')
                MultiplataformaSocket.send(id +'_'+ type_attr +'_hide');
                $('.modal-content').html('<div class="modal-header"><h2>¿Desea comprar '+name_product+'?</h2><button type="button" class="close" data-dismiss="modal"><i class="ti-close"></i></button></div><div class="modal-body"><button type="button" id="sale" class="btn btn-primary btn-md btn-block waves-effect text-center m-b-20">Aceptar</button></div>')
                $("#myModal").modal({show: true})
                $("#sale").on("click", function(event){
                    $(this).prop('disabled', true)
                    $.get('/package/buy/'+id ,function(data){
                        $('.modal-body').html(data)
                        if(type_attr == "True"){
                            MultiplataformaSocket.send(id +'_'+ type_attr +'_reload');
                        }else{
                            MultiplataformaSocket.send(id +'_'+ type_attr +'_remove');
                        }

                    })
                })
            });
        });

        $("#myModal").on("hidden.bs.modal", function () {
           MultiplataformaSocket.send(id +'_'+ type_attr +'_show');
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


