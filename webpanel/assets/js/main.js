//var CONFIG = require('config.json'); <-- require doesn't exist

// convert boot timestamp to user friendly
function convert_uptime(boot_time) {
	var uptime = '';
	
	// TODO
	
	return uptime;
}

$('.tab-section').each(function() {
	$(this).hide();
});

$('#first_tab').show();

function changeSection(id, section) {
	var i, tabcontent, tablinks;
	$('.tab-section').each(function() {
		$(this).hide().fadeOut(50);
	})

	$('.tab').each(function() {
		$(this).removeClass('active');
	})

	$('#' + section).fadeIn(50);
	$('#' + id).addClass('active');
}