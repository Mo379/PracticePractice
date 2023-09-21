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
	M_remove_topic(url, csrf_token, spec_id, module, chapter, topic) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'spec_id=' + spec_id + '&module=' + module;
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&topic=${topic}`
		//sending query to model
		this.xhttp.send(query);
	}
	M_update_topic_list(url, csrf_token, spec_id, module, chapter, order) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&order=${order}`
		//sending query to model
		this.xhttp.send(query);
	}
	M_restore_topic(url, csrf_token, spec_id, module, chapter, topic) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&topic=${topic}`
		//sending query to model
		this.xhttp.send(query);
	}
	M_undelete_topic(url, csrf_token, spec_id, module, chapter, topic) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&topic=${topic}`
		//sending query to model
		this.xhttp.send(query);
	}
	M_erase_topic(url, csrf_token, spec_id, module, chapter, topic) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&topic=${topic}`
		//sending query to model
		this.xhttp.send(query);
	}
	M_update_point_list(url, csrf_token, spec_id, module, chapter, topic, order) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&topic=${topic}&order=${order}`;
		//sending query to model
		this.xhttp.send(query);
	}
	M_remove_point(url, csrf_token, spec_id, module, chapter, topic, point) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&topic=${topic}&point=${point}`;
		//sending query to model
		this.xhttp.send(query);
	}
	M_restore_point(url, csrf_token, spec_id, module, chapter, topic, point) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&topic=${topic}&point=${point}`;
		//sending query to model
		this.xhttp.send(query);
	}
	M_undelete_point(url, csrf_token, spec_id, module, chapter, topic, point) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&topic=${topic}&point=${point}`;
		//sending query to model
		this.xhttp.send(query);
	}
	M_erase_point(url, csrf_token, spec_id, module, chapter, topic, point) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `spec_id=${spec_id}&module=${module}&chapter=${chapter}&topic=${topic}&point=${point}`;
		//sending query to model
		this.xhttp.send(query);
	}
	M_save_prompt_question(url, csrf_token, prompt_id, q_prompt, activated) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `q_prompt_id=${prompt_id}&q_prompt=${q_prompt}`;
		//sending query to model
		this.xhttp.send(query);
	}
	M_save_prompt_topic(url, csrf_token, prompt_id, t_prompt) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `t_prompt_id=${prompt_id}&t_prompt=${t_prompt}`;
		//sending query to model
		this.xhttp.send(query);
	}
	M_save_prompt_point(url, csrf_token, prompt_id, p_prompt, activated) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = `p_prompt_id=${prompt_id}&p_prompt=${p_prompt}`;
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
	C_remove_topic(url, action_url,csrf_token, spec_id, module, chapter, topic) {
		//send command
		// Get a reference to the modal element
		this.M_remove_topic(url, csrf_token, spec_id, module, chapter, topic);
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
						const topic_card = document.getElementById('topic_'+topic);
						const html = `
						  <div class="card course_outline_card mb-2" id='Remove_topic_${topic}'>
						    <div class="card-header course_outline_cell" id="heading-${topic}" style=''>
								<button class="btn text-left">
									<i class="bi bi-arrow-bar-right course_outline_icon"></i> <span id='course_outline_span'>Topic - ${topic}</span>
								</button>
								<button class="btn text-left text-primary" type="button" onclick="controller.C_restore_topic('${action_url}', '${url}', '${csrf_token}', '${spec_id}','${module}', '${chapter}', '${topic}')">
									Restore
								</button>
						    </div>
						  </div>
						`
						const removed_topics = document.getElementById('remove_topic_div');
						removed_topics.innerHTML += html
						topic_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}

	C_update_topic_list(url, csrf_token, spec_id, module, chapter, order) {
		//send command
		// Get a reference to the modal element
		this.M_update_topic_list(url, csrf_token, spec_id, module, chapter, order);
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
	C_restore_topic(url, action_url, csrf_token, spec_id, module, chapter, topic) {
		//send command
		// Get a reference to the modal element
		this.M_restore_topic(url, csrf_token, spec_id, module, chapter, topic);
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
						const topic_card = document.getElementById(`Remove_topic_${topic}`);
						const html = `
						<div class="accordion mb-1" id="topic_${topic}">
						  <div class="card course_outline_card">
						    <div class="card-header course_outline_cell" id="heading-${topic}" style=''>
								<span class='' style='display:inline-block;cursor:pointer;'>
									<input type='hidden' name='ordered_topics[]' value='${topic}'/>
									<span class='handle mr-2 ml-2'style='font-size:25px;'>
										+
									</span>
								</span>
								<button class="btn text-left" style='display:inline-block;' type="button" data-toggle="collapse" data-target="#collapse-${topic}" aria-expanded="true" aria-controls="collapse-${topic}">
									<i class="bi bi-arrow-bar-right course_outline_icon"></i> <span id='course_outline_span'>Topic - ${topic}</span>
								</button>
								<button class="btn text-left text-danger" type="button" onclick="controller.C_remove_topic('${action_url}', '${url}','${csrf_token}', '${spec_id}','${module}', '${chapter}', '${topic}')">
									Remove
								</button>
						    </div>
						    <div id="collapse-${topic}" class="collapse course_outline_collapse" aria-labelledby="heading-${topic}" data-parent="#topic_${topic}">
						      <div class="card-body" style='padding:10px;'>
						      	Refresh to see points!
						      </div>
						    </div>
						  </div>
						</div>
						`
						const topics_list = document.getElementById('topic_list');
						topics_list.innerHTML = html + topics_list.innerHTML
						topic_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}


	C_undelete_topic(url, action_url, second_action_url, csrf_token, spec_id, module, chapter, topic) {
		//send command
		// Get a reference to the modal element
		this.M_undelete_topic(url, csrf_token, spec_id, module, chapter, topic);
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
						const topic_card = document.getElementById(`deleted_topic_${topic}`);
						const html = `
						<div class="accordion mb-1" id="topic_${topic}">
						  <div class="card course_outline_card">
						    <div class="card-header course_outline_cell" id="heading-${topic}" style=''>
								<span class='' style='display:inline-block;cursor:pointer;'>
									<input type='hidden' name='ordered_topics[]' value='${topic}'/>
									<span class='handle mr-2 ml-2'style='font-size:25px;'>
										+
									</span>
								</span>
								<button class="btn text-left" style='display:inline-block;' type="button" data-toggle="collapse" data-target="#collapse-${topic}" aria-expanded="true" aria-controls="collapse-${topic}">
									<i class="bi bi-arrow-bar-right course_outline_icon"></i> <span id='course_outline_span'>Topic - ${topic}</span>
								</button>
								<button class="btn text-left text-danger" type="button" onclick="controller.C_remove_topic('${action_url}', '${second_action_url}','${csrf_token}', '${spec_id}','${module}', '${chapter}', '${topic}')">
									Remove
								</button>
						    </div>
						    <div id="collapse-${topic}" class="collapse course_outline_collapse" aria-labelledby="heading-${topic}" data-parent="#topic_${topic}">
						      <div class="card-body" style='padding:10px;'>
						      	Refresh to see chapters!
						      </div>
						    </div>
						  </div>
						</div>
						`
						const topic_list = document.getElementById('topic_list');
						topic_list.innerHTML = html + topic_list.innerHTML
						topic_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_erase_topic(url, csrf_token, spec_id, module, chapter, topic) {
		//send command
		// Get a reference to the modal element
		this.M_erase_topic(url, csrf_token, spec_id, module, chapter, topic);
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
						const topic_card = document.getElementById(`deleted_topic_${topic}`);
						topic_card.remove();
					}else{
						s.innerHTML = 'error :('
					}
				}, 1000);
			}
		}
	}

	C_update_point_list(url, csrf_token, spec_id, module, chapter, topic, order) {
		//send command
		// Get a reference to the modal element
		this.M_update_point_list(url, csrf_token, spec_id, module, chapter, topic, order);
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
	C_remove_point(url, action_url, chapter_url, csrf_token, spec_id, module, chapter, topic, point, point_title) {
		//send command
		// Get a reference to the modal element
		this.M_remove_point(url, csrf_token, spec_id, module, chapter, topic, point);
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
						const point_card = document.getElementById(`topic_point_${topic}_${point}`);
						const html = `
							<div class='' style='cursor:pointer;' id='Remove_point_${topic}_${point}'>
									<span class='font-weight-bold ml-2' id='course_outline_span'><i class="bi bi-arrow-bar-right course_outline_icon"></i> <a href="${chapter_url}">Point - ${point_title}</a></span>
									<button class="btn text-left text-primary" type="button" onclick="controller.C_restore_point('${action_url}', '${url}','${chapter_url}','${csrf_token}', '${spec_id}','${module}', '${chapter}', '${topic}', '${point}', '${point_title}')">
										Restore
									</button>
							</div>
						`
						const removed_point = document.getElementById(`remove_points_div_${topic}`);
						removed_point.innerHTML += html
						point_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_restore_point(url, action_url, chapter_url, csrf_token, spec_id, module, chapter, topic, point, point_title) {
		//send command
		// Get a reference to the modal element
		this.M_restore_point(url, csrf_token, spec_id, module, chapter, topic, point);
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
						const point_card = document.getElementById(`Remove_point_${topic}_${point}`);
						const html = `
						<div class='' style='cursor:pointer;' id='topic_point_${topic}_${point}'>
								<input type='hidden' name='ordered_points[]' value='${point}'/>
								<span class='point_handle mr-2 ml-5'style='font-size:25px;'>
									+
								</span>
								<span class='font-weight-bold ml-2' id='course_outline_span'><i class="bi bi-arrow-bar-right course_outline_icon"></i> <a href="${chapter_url}">Point - ${point_title}</a></span>
								<button class="btn text-left text-danger" type="button" onclick="controller.C_remove_point('${action_url}', '${url}','${chapter_url}','${csrf_token}', '${spec_id}', '${module}','${chapter}', '${topic}', '${point}', '${point_title}')">
							Remove
							</button>
						</div>
						`
						const point_list = document.getElementById(`point_list_${topic}`);
						point_list.innerHTML = html + point_list.innerHTML
						point_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_undelete_point(url, action_url, second_action_url, chapter_url, csrf_token, spec_id, module, chapter, topic, point, point_title) {
		//send command
		// Get a reference to the modal element
		this.M_undelete_point(url, csrf_token, spec_id, module, chapter, topic, point);
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
						const point_card = document.getElementById(`deleted_point_${topic}_${point}`);
						const html = `
						<div class='' style='cursor:pointer;' id='topic_point_${topic}_${point}'>
								<input type='hidden' name='ordered_points[]' value='${point}'/>
								<span class='point_handle mr-2 ml-5'style='font-size:25px;'>
									+
								</span>
								<span class='font-weight-bold ml-2' id='course_outline_span'><i class="bi bi-arrow-bar-right course_outline_icon"></i> <a href="${chapter_url}">Point - ${point_title}</a></span>
								<button class="btn text-left text-danger" type="button" onclick="controller.C_remove_point('${action_url}', '${second_action_url}','${chapter_url}','${csrf_token}', '${spec_id}', '${module}','${chapter}', '${topic}', '${point}', '${point_title}')">
							Remove
							</button>
						</div>
						`
						const point_list = document.getElementById(`point_list_${topic}`);
						point_list.innerHTML = html + point_list.innerHTML
						point_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_erase_point(url, csrf_token, spec_id, module, chapter, topic, point) {
		//send command
		// Get a reference to the modal element
		this.M_erase_point(url, csrf_token, spec_id, module, chapter, topic, point);
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
						const chapter_card = document.getElementById(`deleted_point_${topic}_${point}`);
						chapter_card.remove();
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_save_prompt_question(url, csrf_token, prompt_id) {
		//send command
		// Get a reference to the modal element
		const q_prompt = document.getElementById(`text_q_prompt_${prompt_id}`).value;
		this.M_save_prompt_question(url, csrf_token, prompt_id, q_prompt);
		var s = document.getElementById(`q_saving_indicator_${prompt_id}`);
		s.innerHTML = 'working...'
		//listen for the repsponse from the server script
		this.xhttp.onreadystatechange = function () {
			if (this.readyState == 4 && this.status == 200) {
				var txt = this.responseText;
				var json = JSON.parse(txt);
				var saving_indic = document.getElementById(`q_saving_indicator_${prompt_id}`);
				saving_indic.innerHTML = 'generating...'
				//
				const request = {
				  'message': json.message.chat,
				  'functions': json.functions,
				  'function_call': json.function_call,
				  'function_app_endpoint': {
				  	...json.function_app_endpoint,
				  },
				  'lambda_url': json.lambda_url
				};
				const handleSubmit = async () => {

				  const response = await fetch(json.lambda_url, {
				    method: "POST",
				    headers: {
				      "Content-Type": "application/json",
				    },
				    body: JSON.stringify(request),
				  });
				  const streamResponse = response.body;
				  if (!streamResponse) {
				    return;
				  }

				  const reader = streamResponse.getReader();
				  const decoder = new TextDecoder();
				  let done = false;
				  let content = "<br><br>";

				  while (true) {
				    const { value } = await reader.read();
				    if (!value) {
				      break;
				    }
				    
				    const chunkValue = decoder.decode(value);
				    content = content + chunkValue;
				    saving_indic.innerHTML = content
				  }
				  return content
				};
				async function run() {
				  try {
				    var content = await handleSubmit();
					
				  } catch (error) {
				    console.error('An error occurred:', error);
				    loading(false)
				  }
				}
				run()
			}
		}
	}
	C_save_prompt_topic(url, csrf_token, prompt_id) {
		//send command
		// Get a reference to the modal element
		const t_prompt = document.getElementById(`text_t_prompt_${prompt_id}`).value;
		this.M_save_prompt_topic(url, csrf_token, prompt_id, t_prompt);
		var s = document.getElementById(`t_saving_indicator_${prompt_id}`);
		s.innerHTML = 'saving...'
		//listen for the repsponse from the server script
		this.xhttp.onreadystatechange = function () {
			if (this.readyState == 4 && this.status == 200) {
				var txt = this.responseText;
				var json = JSON.parse(txt);
				setTimeout(function (){
					var s = document.getElementById(`t_saving_indicator_${prompt_id}`);
					if (json.error == 0){
						s.innerHTML = 'all saved'
					}else{
						s.innerHTML = 'error :('
					}

				}, 1000);
			}
		}
	}
	C_save_prompt_point(url, csrf_token, prompt_id) {
		//send command
		// Get a reference to the modal element
		const p_prompt = document.getElementById(`text_p_prompt_${prompt_id}`).value;
		this.M_save_prompt_point(url, csrf_token, prompt_id, p_prompt);
		var s = document.getElementById(`p_saving_indicator_${prompt_id}`);
		s.innerHTML = 'working...'
		//listen for the repsponse from the server script
		this.xhttp.onreadystatechange = function () {
			if (this.readyState == 4 && this.status == 200) {
				var txt = this.responseText;
				var json = JSON.parse(txt);
				var saving_indic = document.getElementById(`p_saving_indicator_${prompt_id}`);
				saving_indic.innerHTML = 'generating...'
				//
				const request = {
				  'message': json.message.chat,
				  'functions': json.functions,
				  'function_call': json.function_call,
				  'function_app_endpoint': {
				  	...json.function_app_endpoint,
				  },
				  'lambda_url': json.lambda_url
				};
				const handleSubmit = async () => {

				  const response = await fetch(json.lambda_url, {
				    method: "POST",
				    headers: {
				      "Content-Type": "application/json",
				    },
				    body: JSON.stringify(request),
				  });
				  const streamResponse = response.body;
				  if (!streamResponse) {
				    return;
				  }

				  const reader = streamResponse.getReader();
				  const decoder = new TextDecoder();
				  let done = false;
				  let content = "<br><br>";

				  while (true) {
				    const { value } = await reader.read();
				    if (!value) {
				      break;
				    }
				    
				    const chunkValue = decoder.decode(value);
				    content = content + chunkValue;
				    saving_indic.innerHTML = content
				  }
				  return content
				};
				async function run() {
				  try {
				    var content = await handleSubmit();
					
				  } catch (error) {
				    console.error('An error occurred:', error);
				    loading(false)
				  }
				}
				run()
			}
		}
	}
}









view = new view();
controller = new controller(view);
