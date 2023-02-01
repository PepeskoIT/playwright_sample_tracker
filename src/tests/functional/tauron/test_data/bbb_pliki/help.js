$(function(){
	$('div.help:not(.active)>p').click(function(){
		setTimeout(function(){
			$('.help').addClass('active');
		}, 10);
	});
	$('body').click(function(e){
		if($('.help.active').length && !$(e.target).parents('.help-body').length && !$(e.target).is('.help-body'))
		{
			$('.help.active').removeClass('active');
		}
	});

	$('body').on('click', '.newsletter-submit', function(e){
		e.preventDefault();
		are_checked = true;
		$('.newsletter_agree').each(function(){
			if(!$(this).prop('checked'))
			{
				are_checked = false;
			}
		});
		if(!are_checked)
		{
			swal({
				html: 'Aby zapisać się na newsletter wszystkie zgody są wymagane',
				type: 'error',
				confirmButtonColor: '#E2007A',
				cancelButtonColor: '#AAAAAA',
				customClass: 'newsletter-add'
			}).then(function(){
				setTimeout(function(){
					$('.help').addClass('active');
				}, 10);
			});
		}
		else
		{
			$.ajax({
				url: '/frontend/newsletter/ajaxSaveEmail',
				type: "POST",
				cache: false,
				dataType: "json",
				data: {'newsletter': $('#newsletter_email').val()},
				success: function(data) {
					if (data.status == 'success'){
						swal({
							html: data.msg,
							type: 'info',
							confirmButtonColor: '#E2007A',
							confirmButtonText: 'Zamknij',
							cancelButtonColor: '#AAAAAA',
							customClass: 'newsletter-add'
						}).then(function(){
							setTimeout(function(){
								$('#newsletter_email').val('');
								$('.newsletter_agree').prop('checked', false);
							}, 10);
						});
					} else if (data.status == 'error'){
						swal({
							html: data.msg[0],
							type: 'error',
							confirmButtonColor: '#E2007A',
							cancelButtonColor: '#AAAAAA',
							customClass: 'newsletter-add'
						}).then(function(){
							setTimeout(function(){
								$('.help').addClass('active');
							}, 10);
						});
					}
				},
				error: function () {
					console.log('Wystąpił błąd podczas dodawania do newslettera');
				}
			});
		}
	});
});