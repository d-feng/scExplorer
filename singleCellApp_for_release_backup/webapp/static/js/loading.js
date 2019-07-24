

function loading1_start(div){
	
	$(div).html('<div style="margin: 0;position: absolute;top: 30%; left: 40%"><div class="cssload-loader"><div class="cssload-inner cssload-one"></div><div class="cssload-inner cssload-two"></div><div class="cssload-inner cssload-three"></div></div></div>');
}

function loading1_end(div){
	$(div).html('');
}