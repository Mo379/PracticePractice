//coommunicates with php and gets a result to be displayed as a view
class xhttp {
	open_port(url) {
		this.xhttp = new XMLHttpRequest();
		this.xhttp.open('POST', url, true);
		this.xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	}
}
//

class view {
	//loading
	alert_loading() {
		alert('loading');
	};
}
//coommunicates with server and gets a result to be displayed as a view
class model extends xhttp {
	//
	M_remove_module(url, csrf_token, spec_id, module) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&module=' + module;
		//sending query to model
		this.xhttp.send(query);
	}
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
	constructor(view) {
		super();
		this.view = view;
	}
	//add new spec moduel
	C_remove_module(url, csrf_token, spec_id, module) {
		//send command
		// Get a reference to the modal element
		this.M_remove_module(url, csrf_token, spec_id, module);
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
						const module_card = document.getElementById('Module_'+module);
						const html = `
						  <div class="card course_outline_card mb-2">
						    <div class="card-header course_outline_cell" id="heading-${module}" style=''>
								<button class="btn text-left">
									<i class="bi bi-arrow-bar-right course_outline_icon"></i> <span id='course_outline_span'>Module - ${module}</span>
								</button>
								<button class="btn text-left text-primary" type="button">
									Restore
								</button>
						    </div>
						  </div>
						`
						const removed_modules = document.getElementById('remove_modules_div');
						removed_modules.innerHTML += html
						module_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
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









view = new view();
controller = new controller(view);
