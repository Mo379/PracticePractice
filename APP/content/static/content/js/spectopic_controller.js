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
	M_restore_module(url, csrf_token, spec_id, module) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&module=' + module;
		//sending query to model
		this.xhttp.send(query);
	}
	M_undelete_module(url, csrf_token, spec_id, module) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&module=' + module;
		//sending query to model
		this.xhttp.send(query);
	}
	M_erase_module(url, csrf_token, spec_id, module) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&module=' + module;
		//sending query to model
		this.xhttp.send(query);
	}
	M_update_chapter_list(url, csrf_token, spec_id, module, order) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&order=${order}`;
		//sending query to model
		this.xhttp.send(query);
	}
	M_remove_chapter(url, csrf_token, spec_id, module, chapter) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&module=' + module + '&chapter='+ chapter;
		//sending query to model
		this.xhttp.send(query);
	}
	M_restore_chapter(url, csrf_token, spec_id, module, chapter) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&module=' + module + "&chapter=" + chapter;
		//sending query to model
		this.xhttp.send(query);
	}
	M_undelete_chapter(url, csrf_token, spec_id, module, chapter) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&module=' + module + "&chapter=" + chapter;
		//sending query to model
		this.xhttp.send(query);
	}
	M_erase_chapter(url, csrf_token, spec_id, module, chapter) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&module=' + module + "&chapter=" + chapter;
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
	C_remove_module(url, action_url,csrf_token, spec_id, module) {
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
						  <div class="card course_outline_card mb-2" id='Remove_module_${module}'>
						    <div class="card-header course_outline_cell" id="heading-${module}" style=''>
								<button class="btn text-left">
									<i class="bi bi-arrow-bar-right course_outline_icon"></i> <span id='course_outline_span'>Module - ${module}</span>
								</button>
								<button class="btn text-left text-primary" type="button" onclick="controller.C_restore_module('${action_url}', '${url}', '${csrf_token}', '${spec_id}','${module}')">
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
	C_restore_module(url, action_url, csrf_token, spec_id, module) {
		//send command
		// Get a reference to the modal element
		this.M_restore_module(url, csrf_token, spec_id, module);
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
						const module_card = document.getElementById(`Remove_module_${module}`);
						const html = `
						<div class="accordion mb-1" id="Module_${module}">
						  <div class="card course_outline_card">
						    <div class="card-header course_outline_cell" id="heading-${module}" style=''>
								<span class='' style='display:inline-block;cursor:pointer;'>
									<input type='hidden' name='ordered_modules[]' value='${module}'/>
									<span class='handle mr-2 ml-2'style='font-size:25px;'>
										+
									</span>
								</span>
								<button class="btn text-left" style='display:inline-block;' type="button" data-toggle="collapse" data-target="#collapse-${module}" aria-expanded="true" aria-controls="collapse-${module}">
									<i class="bi bi-arrow-bar-right course_outline_icon"></i> <span id='course_outline_span'>Module - ${module}</span>
								</button>
								<button class="btn text-left text-danger" type="button" onclick="controller.C_remove_module('${action_url}', '${url}','${csrf_token}', '${spec_id}','${module}')">
									Remove
								</button>
						    </div>
						    <div id="collapse-${module}" class="collapse course_outline_collapse" aria-labelledby="heading-${module}" data-parent="#Module_${module}">
						      <div class="card-body" style='padding:10px;'>
						      	Refresh to see chapters!
						      </div>
						    </div>
						  </div>
						</div>
						`
						const modules_list = document.getElementById('modules_list');
						modules_list.innerHTML = html + modules_list.innerHTML
						module_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}


	C_undelete_module(url, action_url, second_action_url, csrf_token, spec_id, module) {
		//send command
		// Get a reference to the modal element
		this.M_undelete_module(url, csrf_token, spec_id, module);
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
						const module_card = document.getElementById(`deleted_module_${module}`);
						const html = `
						<div class="accordion mb-1" id="Module_${module}">
						  <div class="card course_outline_card">
						    <div class="card-header course_outline_cell" id="heading-${module}" style=''>
								<span class='' style='display:inline-block;cursor:pointer;'>
									<input type='hidden' name='ordered_modules[]' value='${module}'/>
									<span class='handle mr-2 ml-2'style='font-size:25px;'>
										+
									</span>
								</span>
								<button class="btn text-left" style='display:inline-block;' type="button" data-toggle="collapse" data-target="#collapse-${module}" aria-expanded="true" aria-controls="collapse-${module}">
									<i class="bi bi-arrow-bar-right course_outline_icon"></i> <span id='course_outline_span'>Module - ${module}</span>
								</button>
								<button class="btn text-left text-danger" type="button" onclick="controller.C_remove_module('${action_url}', '${second_action_url}','${csrf_token}', '${spec_id}','${module}')">
									Remove
								</button>
						    </div>
						    <div id="collapse-${module}" class="collapse course_outline_collapse" aria-labelledby="heading-${module}" data-parent="#Module_${module}">
						      <div class="card-body" style='padding:10px;'>
						      	Refresh to see chapters!
						      </div>
						    </div>
						  </div>
						</div>
						`
						const modules_list = document.getElementById('modules_list');
						modules_list.innerHTML = html + modules_list.innerHTML
						module_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_erase_module(url, csrf_token, spec_id, module) {
		//send command
		// Get a reference to the modal element
		this.M_erase_module(url, csrf_token, spec_id, module);
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
						const module_card = document.getElementById(`deleted_module_${module}`);
						module_card.remove();
					}else{
						s.innerHTML = 'error :('
					}
				}, 1000);
			}
		}
	}

	C_update_chapter_list(url, csrf_token, spec_id, module, order) {
		//send command
		// Get a reference to the modal element
		this.M_update_chapter_list(url, csrf_token, spec_id, module, order);
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
	C_remove_chapter(url, action_url, chapter_url, csrf_token, spec_id, module, chapter) {
		//send command
		// Get a reference to the modal element
		this.M_remove_chapter(url, csrf_token, spec_id, module, chapter);
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
						const chapter_card = document.getElementById(`module_chapter_${module}_${chapter}`);
						const html = `
							<div class='' style='cursor:pointer;' id='Remove_chapter_${module}_${chapter}'>
									<span class='font-weight-bold ml-2' id='course_outline_span'><i class="bi bi-arrow-bar-right course_outline_icon"></i> <a href="${chapter_url}">Chapter - ${chapter}</a></span>
									<button class="btn text-left text-primary" type="button" onclick="controller.C_restore_chapter('${action_url}', '${url}','${chapter_url}','${csrf_token}', '${spec_id}','${module}', '${chapter}')">
										Restore
									</button>
							</div>
						`
						const removed_modules = document.getElementById(`remove_chapters_div_${module}`);
						removed_modules.innerHTML += html
						chapter_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_restore_chapter(url, action_url, chapter_url, csrf_token, spec_id, module, chapter) {
		//send command
		// Get a reference to the modal element
		this.M_restore_chapter(url, csrf_token, spec_id, module, chapter);
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
						const chapter_card = document.getElementById(`Remove_chapter_${module}_${chapter}`);
						const html = `
						<div class='' style='cursor:pointer;' id='module_chapter_${module}_${chapter}'>
								<input type='hidden' name='ordered_chapters[]' value='${chapter}'/>
								<span class='chapter_handle mr-2 ml-5'style='font-size:25px;'>
									+
								</span>
								<span class='font-weight-bold ml-2' id='course_outline_span'><i class="bi bi-arrow-bar-right course_outline_icon"></i> <a href="${chapter_url}">Chapter - ${chapter}</a></span>
								<button class="btn text-left text-danger" type="button" onclick="controller.C_remove_chapter('${action_url}', '${url}','${chapter_url}','${csrf_token}', '${spec_id}', '${module}','${chapter}')">
							Remove
							</button>
						</div>
						`
						const chapter_list = document.getElementById(`chapter_list_${module}`);
						chapter_list.innerHTML = html + chapter_list.innerHTML
						chapter_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_undelete_chapter(url, action_url, second_action_url, chapter_url, csrf_token, spec_id, module, chapter) {
		//send command
		// Get a reference to the modal element
		this.M_undelete_chapter(url, csrf_token, spec_id, module, chapter);
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
						const chapter_card = document.getElementById(`deleted_chapter_${module}_${chapter}`);
						const html = `
						<div class='' style='cursor:pointer;' id='module_chapter_${module}_${chapter}'>
								<input type='hidden' name='ordered_chapters[]' value='${chapter}'/>
								<span class='chapter_handle mr-2 ml-5'style='font-size:25px;'>
									+
								</span>
								<span class='font-weight-bold ml-2' id='course_outline_span'><i class="bi bi-arrow-bar-right course_outline_icon"></i> <a href="${chapter_url}">Chapter - ${chapter}</a></span>
								<button class="btn text-left text-danger" type="button" onclick="controller.C_remove_chapter('${action_url}', '${second_action_url}','${chapter_url}','${csrf_token}', '${spec_id}', '${module}','${chapter}')">
							Remove
							</button>
						</div>
						`
						const chapter_list = document.getElementById(`chapter_list_${module}`);
						chapter_list.innerHTML = html + chapter_list.innerHTML
						chapter_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_erase_chapter(url, csrf_token, spec_id, module, chapter) {
		//send command
		// Get a reference to the modal element
		this.M_erase_chapter(url, csrf_token, spec_id, module, chapter);
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
						const chapter_card = document.getElementById(`deleted_chapter_${module}_${chapter}`);
						chapter_card.remove();
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
