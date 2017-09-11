String.prototype.replaceAll = function(search, replacement) {
    var target = this;
    return target.replace(new RegExp(search, 'g'), replacement);
};

// convert boot timestamp to user friendly
function convert_uptime(bootTime) {
	var time = bootTime.split(' ')[0].split('/');
	var fixedBootTime = new Date('20' + time[2] + '-' + time[0] + '-' + time[1] + 'T' + bootTime.split(' ')[1]);
	var diffDate = new Date(new Date() - fixedBootTime);

	var delta = diffDate / 1000;
	var days = Math.floor(delta / 86400);
	delta -= days * 86400;
	var hours = Math.floor(delta / 3600) % 24;
	delta -= hours * 3600;
	var minutes = Math.floor(delta / 60) % 60;
	delta -= minutes * 60;
	var seconds = delta % 60;

	return '' + days + ' days, ' + ('0' + hours).slice(-2) + ':' + ('0' + minutes).slice(-2) + ':' + ('0' + seconds).slice(-2);
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

// get CSS icon based on label
function get_icon(label) {
	var type = '';
	switch(label) {
		case 'GN':
			type = 'server';
			break;
		case 'DB':
			type = 'database';
			break;
		case 'EM':
			type = 'envelope';
			break;
		case 'WB':
			type = 'internet-explorer';
			break;
		case 'FW':
			type = 'fire';
			break;
		case 'AD':
			type = 'users';
			break;
		case 'VM':
			type = 'desktop';
			break;
		case 'FS':
			type = 'folder';
			break;
		case 'SY':
			type = 'lock';
			break;
		case 'MN':
			type = 'search';
			break;
		default:
			type = 'question';
			break;
	}
	return type;
}

// get name based on label
function get_type_name(label) {
	var type = '';
	switch(label) {
		case 'GN':
			type = 'General Server';
			break;
		case 'DB':
			type = 'Database Server';
			break;
		case 'EM':
			type = 'Email Server';
			break;
		case 'WB':
			type = 'Website Server';
			break;
		case 'FW':
			type = 'Firewall';
			break;
		case 'AD':
			type = 'Active Directory Server';
			break;
		case 'VM':
			type = 'Hypervisor Server';
			break;
		case 'FS':
			type = 'File Share Server';
			break;
		case 'SY':
			type = 'Security Server';
			break;
		case 'MN':
			type = 'Monitoring Server';
			break;
		default:
			type = 'Unknown Server';
			break;
	}
	return type;
}