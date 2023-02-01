var finaleDate;

$(window).on('load', function(){

    ////////////////////////
    // główny template
    ////////////////////////
    var header = $('nav');

    $(window).resize(function(){
        $('body').css('padding-top', header.outerHeight()+20);
    }).resize();

    $(window).scroll(function(){
        // zakomentowane per Jira #SKLEPW-290
//        if($(window).scrollTop() >= header.outerHeight()) {
//            if(!header.hasClass('sticked')) {
//                header.addClass('sticked');
//            }
//        } else {
//            header.removeClass('sticked');
//        }

        $('body').css('padding-top', header.outerHeight()+20);

//        if($('.backtrop').is(':visible')) {
//            $('.backtrop').click();
//        }

    }).scroll();

    //////////////////////
    // Klawisz delete
    /////////////////////
    $('a.delete').on('click', function(ev){
        ev.preventDefault();
        
        var button = $(this);
        
        swal({
            title: '',
            text: "Proszę o potwierdzenie usunięcia elementu",
            type: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#E2007A',
            cancelButtonColor: '#AAAAAA',
            confirmButtonText: 'Usuń',
            cancelButtonText: 'Anuluj'
          }
        ).then(
            function(){
                window.location = button.attr('href');
            }
        );
    });

	
	$("form.block-press-enter").keypress(function(e) {
	  //Enter key
	  if (e.which == 13) {
		return false;
	  }
	});

    $('body').on('click','.radio-box',function(){
        gray_checkbox();
    });

    var date = $('.countdown').data('date-to');
    if(date)
    {
        finaleDate = new Date(date);
		var clock = setInterval(countdown_clock, 1000);
		countdown_clock();
    }

    gray_checkbox();

	$('.our-submenu-dropdown [data-toggle="dropdown"]').click(function(e){
		$(this).parent().toggleClass('open');
		e.preventDefault();
	});
});

function countdown_clock()
{
	var currentDate = new Date();
	var diff = finaleDate.getTime() - currentDate.getTime();

	if(diff > 0)
	{
		$('.countdown .days').html(('0' + Math.floor(diff / (1000 * 60 * 60 * 24))).slice(-2));
		$('.countdown .hours').html(('0' + Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))).slice(-2));
		$('.countdown .minutes').html(('0' + Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))).slice(-2));
		$('.countdown .seconds').html(('0' + Math.floor((diff % (1000 * 60)) / 1000)).slice(-2));
	}
	else
	{
		$('.countdown').fadeOut();
		clearInterval(clock);
	}
}

function gray_checkbox()
{
    $('.radio-box').each(function(){
        var radio_btn = $(this).find('input[type="radio"]');
        if (radio_btn.is(':checked')){
            $(this).addClass('radio-gray-box');
        } else {
            $(this).removeClass('radio-gray-box');
        }
    });
}

function play_video(title, url, type, html) {
    var video_html = "";
    if (type == "yt") {
        video_html = "<iframe class=\"iframe_yt\" src=\"" + url + "\" frameborder=\"0\" allow=\"accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture\" allowfullscreen></iframe>";
    } else {
        video_html = "<video width=\"100%\" height=\"100%\" controls>" +
                "<source src=\"/" + url + "\"  type=\"" + type + "\">" +
                " Your browser doesn't support HTML5 video tag.</video>";
    }
    swal({
        title: '<strong>' + title + '</strong>',
        icon: 'info',
        width: '80%',
        html: video_html + html,
        showConfirmButton: false,
        showCloseButton: true,
        onClose: onClose
    });

    function onClose() {
        clean_video();
        swal.close();
    }
}

function clean_video() {
    swal({
        title: '<strong>?</strong>',
        icon: 'info',
        width: '80%',
        html:
                "<div>720</div>",
        showConfirmButton: false,
        showCloseButton: true
    });
}
