//coommunicates with php and gets a result to be displayed as a view
class xhttp {
	open_port(url) {
		this.xhttp = new XMLHttpRequest();
		this.xhttp.open('POST', url, true);
		this.xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	}
}
//coommunicates with server and gets a result to be displayed as a view
class model extends xhttp {
	//
	M_update_module_list(url, csrf_token, spec_id, order) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&order=' + order;
		//sending query to model
		this.xhttp.send(query);
	}
}

//used by the user, tells the model to do something. this class is both a controller and a view
class controller extends model {
	//construct
	constructor() {
		super();
	}

	C_update_module_list(url, csrf_token, spec_id, order) {
		//send command
		// Get a reference to the modal element
		this.M_update_module_list(url, csrf_token, spec_id, order);
		var s = document.getElementById('saving_indicator');
		s.innerHTML = 'saving...'
		//listen for the repsponse from the server script
		this.xhttp.onreadystatechange = function () {
			if (this.readyState == 4 && this.status == 200) {
				var txt = this.responseText;
				var json = JSON.parse(txt);
				setTimeout(function (){
					var s = document.getElementById('saving_indicator');
					if (json.error == 0){
						s.innerHTML = 'all saved'
					}else{
						s.innerHTML = 'error :('
					}
				}, 1000);
			}
		}
	}
}
controller = new controller();
