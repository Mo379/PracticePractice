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
	//
	constructor(){
		this.spinner = '<button id="loading_spinner" type="button" disabled><span class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span><br>Loading...</button>';
	}
	alert_loading() {
		alert('loading');
	};
	alert_load_lesson() {
		var s = document.getElementById('main_chat_scroll_container');
		s.innerHTML = this.spinner; 
	};
}
//coommunicates with server and gets a result to be displayed as a view
class model extends xhttp {
	//
	M_next_point(url, csrf_token, course_version_id, part_id, point_id) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'course_version_id='+ course_version_id +'&part_id=' + part_id + '&point_id=' + point_id;
		//sending query to model
		this.xhttp.send(query);
	}
	M_init_prompt(url, csrf_token, part_id, point_id, order_id, user_prompt){
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'part_id=' + part_id + '&point_id=' + point_id + '&order_id=' + order_id + '&user_prompt=' + user_prompt;
		//sending query to model
		this.xhttp.send(query);
	}
}

//used by the user, tells the model to do something. this class is both a controller and a view
class controller extends model {
	//construct
	constructor(util, view) {
		super();
		this.util = util;
		this.view = view;
	}
	//add new spec moduel
	C_ask_from_book(url, csrf_token, book_item_id, random_id, point_id, part_id) {
		const element = document.getElementById(book_item_id);
		// Create a new element
		const newElement = document.createElement("div");
		if ($(`#ask_${point_id}_${random_id}`).length == 0){
			newElement.innerHTML = `
				<div class='AI_chat_text AI_text_user chat_thread_${point_id}' id='ask_${point_id}_${random_id}'>
					<div class='AI_text_wrap'>
						<div class='AI_text_image'>
							<i class="bi bi-send-fill"style='color: var(--text-color-1);'></i>
						</div>
						<div class='AI_text_text' id='ask_content_${point_id}_${random_id}'>
							<textarea class="form-control bg-transparent mb-3 AI_user_text_area" id='user_input_${point_id}_${random_id}'style="color: var(--text-color-1);">Prompt here...</textarea>
							<p class='d-none' id='display_user_input_${point_id}_${random_id}'></p>
							<div class='AI_window_typing'>
								<div style='margin:auto;'>
								<button 
									class='btn btn-success'
									id='submit_${point_id}_${random_id}'
									onclick='Controller.C_init_prompt("${url}", "${csrf_token}","${random_id}", "${point_id}", "${part_id}", "${random_id}")'
								>
									<p id='button_text_${point_id}_${random_id}' style='margin:0;'>Prompt <i class="bi bi-send"></i></p>
									<div id='spinner_and_wait_${point_id}_${random_id}' class='d-none'>
										<div class="d-flex justify-content-center">
										  <div class="spinner-border spinner-border-sm" role="status">
										    <span class="sr-only">Loading...</span>
										  </div>
										</div>
									</div>
								</button>
								<button class='btn btn-secondary' id='cancel_prompt_${point_id}_${random_id}' onclick='Controller.C_cancel_ask("ask_${point_id}_${random_id}", "ask_button_${point_id}")'>
									Cancel
								</button>
								</div>
							</div>
						</div>
					</div>
				</div>
				`;

			// Insert the new element below the specified element
			element.insertAdjacentElement("afterend", newElement);
			document.querySelector(`#ask_button_${point_id}`).classList.add("d-none");
		}
		//listen for the repsponse from the server script
	}
	C_next_point(url, url_prompt, csrf_token, self_element_id, parent_element_id, course_version_id, part_id, point_iid,point_id, num_next_points, ordered_list_id){
		const utility = this.util

		const next_point_button = document.getElementById(self_element_id);
		next_point_button.remove()
		this.M_next_point(url, csrf_token, course_version_id, part_id, point_id);
		this.xhttp.onreadystatechange = function () {
			if (this.readyState == 4 && this.status == 200) {
				var txt = this.responseText;
				var json = JSON.parse(txt);
				setTimeout(function (){
					if (json.error == 0){
						var html_content = json.message
						var html_videos = json.videos_html
						var script_text = json.script_html
						var tags_videos = json.videos_tags
						var new_tag = json.new_tag
						var relevant_part_id = json.relevant_part_id
						var new_point_id = json.new_point_id
						var new_point_unique = json.new_point_unique
						var new_topic = json.new_topic
						num_next_points = Number(num_next_points) - 1
						ordered_list_id = Number(ordered_list_id)
						// 
						const scriptElement = document.createElement('script');
						scriptElement.textContent = script_text;
						//
						var videos_buttons = ''
						for(var i = 0; i < tags_videos.length; i++){
							var vid_unique = tags_videos[i];
							var button_html = `
							<button id='link-${vid_unique}' type="button" class="btn btn-primary mb-3"
								style='display:inline;margin-left:auto;'>
								<i class="bi bi-caret-right-square-fill"></i>
							</button>
							`
							videos_buttons += button_html
						}
						if (new_topic){
							var element = document.getElementById(`topic_id_${new_topic}`);
						}else{
							//var element = document.getElementById(parent_element_id);
							// Assuming you want to get the last element of the "example-class" ordered class
							var elements = document.querySelectorAll(`.chat_thread_${point_iid}`);
							// Get the last element
							var element = elements[elements.length - 1];
						}
						// Create a new element
						const newElement = document.createElement("div");
						newElement.innerHTML = `
							<div class='AI_chat_text AI_text_ai chat_thread_${new_point_id}' id='text_book_${new_tag}'>
								<div class='AI_text_wrap'>
									<div class='AI_text_image'>
										<i class="bi bi-book"></i>
									</div>
									<div class='AI_text_text'>
										${videos_buttons}
										<div class='mb-3' id='AI_text_introduction_${new_tag}'>
										</div>
										<div class='AI_window_typing'>
												<div style='margin:auto;' id='buttons_container_${new_tag}'>
											<button class='btn btn-primary' id='ask_button_${new_point_id}' onclick='Controller.C_ask_from_book("${url_prompt}", "${csrf_token}", "text_book_${new_tag}", "${ordered_list_id}", "${new_point_id}", "${part_id}")'>
												Ask
											</button>
											</div>
										</div>
									</div>
									<script>
									</script>
								</div>
							</div>
							`;

						// Insert the new element below the specified element
						let next_button = `
						<button
							id='next_point_button_${new_tag}'
							class='btn btn-success'
							onclick='Controller.C_next_point("${url}", "${url_prompt}","${csrf_token}", "next_point_button_${new_tag}", "text_book_${new_tag}", "${course_version_id}","${relevant_part_id}", "${new_point_id}","${new_point_unique}", ${num_next_points},${Number(ordered_list_id) + 1})'
						>
							Next point (${num_next_points})
						</button>
						`
						element.insertAdjacentElement("afterend", newElement);
						const videos_container = document.createElement('span');
						videos_container.innerHTML = html_videos;
						document.getElementById('AI_window_chat_id').appendChild(videos_container)
						document.getElementById('AI_window_chat_id').appendChild(scriptElement);
						utility.write(`AI_text_introduction_${new_tag}`, html_content)
						if (num_next_points > 0){
							document.getElementById(`buttons_container_${new_tag}`).innerHTML += next_button;
						}
					}else{
					}

				}, 1000);
			}
		}
	}
	C_init_prompt(url, csrf_token, random_id, point_id, part_id, order_id){
		const utility = this.util
		// Get the textarea element
		var textarea = document.getElementById(`user_input_${point_id}_${random_id}`);
		var display_textarea = document.getElementById(`display_user_input_${point_id}_${random_id}`);
		// Get the value of the textarea
		var textareaValue = textarea.value;
		display_textarea.innerHTML = textareaValue
		//
		var loading = function(isLoading) {
		      if (isLoading) {
			// Disable the button and show a spinner
			document.querySelector(`#submit_${point_id}_${random_id}`).disabled = true;
			document.querySelector(`#user_input_${point_id}_${random_id}`).classList.add("d-none");
			document.querySelector(`#display_user_input_${point_id}_${random_id}`).classList.remove("d-none");
			document.querySelector(`#cancel_prompt_${point_id}_${random_id}`).disabled = true;
			document.querySelector(`#spinner_and_wait_${point_id}_${random_id}`).classList.remove("d-none");
			document.querySelector(`#button_text_${point_id}_${random_id}`).classList.add("d-none");
		      } else {
			document.querySelector(`#submit_${point_id}_${random_id}`).disabled = false;
			document.querySelector(`#user_input_${point_id}_${random_id}`).classList.remove("d-none");
			document.querySelector(`#display_user_input_${point_id}_${random_id}`).classList.add("d-none");
			document.querySelector(`#cancel_prompt_${point_id}_${random_id}`).disabled = false;
			document.querySelector(`#spinner_and_wait_${point_id}_${random_id}`).classList.add("d-none");
			document.querySelector(`#button_text_${point_id}_${random_id}`).classList.remove("d-none");
		      }
		};
		MathJax.typeset()

		this.M_init_prompt(url, csrf_token, part_id, point_id, order_id, textareaValue);
		const old_object = this
		loading(true)
		this.xhttp.onreadystatechange = function () {
			if (this.readyState == 4 && this.status == 200) {
				var txt = this.responseText;
				var json = JSON.parse(txt);
				//
				const request = {
				  'message': json.message,
				  'part_id': json.part_id,
				  'point_id': json.point_id,
				  'order_id': json.order_id
				};
				//
				AWS.config.update({region: 'eu-north-1'});
				AWS.config.credentials = new AWS.CognitoIdentityCredentials({IdentityPoolId: 'eu-north-1:539f7067-2405-4e41-8aed-a62ee033f30c'});

				var pullReturned = null;
				var slotResults;
				var isSpinning = false;

				// Prepare to call Lambda function.
				var lambda = new AWS.Lambda({region: 'eu-west-2', apiVersion: '2015-03-31'});
				var pullParams = {
					FunctionName : 'OpenAI-ChatGPT-Turbo',
					InvocationType : 'RequestResponse',
					LogType : 'None',
					Payload: JSON.stringify(request)
				};
				lambda.invoke(pullParams, function(err, data) {
					if (err) {
						loading(false)
					} else {
						const response = JSON.parse(data.Payload)
						if (response.StatusCode == 200){
							const element = document.getElementById(`ask_${point_id}_${random_id}`);
							const newElement = document.createElement("div");
							newElement.innerHTML = `
								<div class='AI_chat_text AI_text_ai chat_thread_${point_id}' id='ai_response_${random_id}'>
									<div class='AI_text_wrap'>
										<div class='AI_text_image'>
											<i class="bi bi-robot"></i>
										</div>
										<div class='AI_text_text'>
											<div class='mb-3' id='AI_text_response_${point_id}_${random_id}'>
											</div>
											<div class='AI_window_typing'>
												<div style='margin:auto;'>
													<button class='btn btn-primary' id='ask_button_${point_id}_${random_id}' onclick='Controller.C_ask_from_book("{%url "AI:_ask_from_book"%}", "{{csrf_token}}", "text_book_{{random_id}}", "{{ forloop.counter }}", "{{point_id}}", "{{part.id}}")'>
													<button class='btn btn-primary' id='ask_button_${point_id}_${random_id}' onclick='Controller.C_ask_from_book("${url_prompt}", "${csrf_token}", "text_book_${new_tag}", "${ordered_list_id}", "${new_point_id}", "${part_id}")'>
													Ask
												</button>
											</div>
										</div>
									</div>
								</div>
								`;
							element.insertAdjacentElement("afterend", newElement);
							document.querySelector(`#submit_${point_id}_${random_id}`).classList.add("d-none")
							document.querySelector(`#cancel_prompt_${point_id}_${random_id}`).classList.add("d-none")
							utility.write(`AI_text_response_${point_id}_${random_id}`, response.body)
						}else{
							alert(response.StatusCode)
							loading(false)
						}
					}
				});
			}
		}
	}
	//add new spec moduel
	C_cancel_ask(ask_item_id, ask_button_id) {
		const element = document.getElementById(ask_item_id);
		element.remove();
		document.querySelector(`#${ask_button_id}`).classList.remove("d-none");
	}
}









util = new util();
view = new view();
Controller = new controller(util, view);
