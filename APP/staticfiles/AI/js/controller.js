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
	C_ask_from_book(book_item_id) {
		const element = document.getElementById(book_item_id);
		// Create a new element
		const newElement = document.createElement("div");
		newElement.innerHTML = `
			<div class='AI_chat_text AI_text_user' id='ask_id'>
				<div class='AI_text_wrap'>
					<div class='AI_text_image'>
						<i class="bi bi-send-fill"style='color: var(--text-color-1);'></i>
					</div>
					<div class='AI_text_text'>
						<textarea class="form-control bg-transparent mb-3 AI_user_text_area" style="color: var(--text-color-1);">type here...</textarea>
						<div class='AI_window_typing'>
							<div style='margin:auto;'>
							<button class='btn btn-success'>
								Save & Submit
							</button>
							<button class='btn btn-secondary' onclick='Controller.C_cancel_ask("ask_id")'>
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
		//listen for the repsponse from the server script
	}
	C_next_point(url, csrf_token, self_element_id, parent_element_id, course_version_id, part_id,point_id){
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
						var new_topic = json.new_topic
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
							var element = document.getElementById(parent_element_id);
						}
						// Create a new element
						const newElement = document.createElement("div");
						newElement.innerHTML = `
							<div class='AI_chat_text AI_text_ai' id='text_book_${new_tag}'>
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
											<button class='btn btn-primary' onclick='Controller.C_ask_from_book("text_book_${new_tag}")'>
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
							onclick='Controller.C_next_point("${url}", "${csrf_token}", "next_point_button_${new_tag}", "text_book_${new_tag}", "${course_version_id}","${relevant_part_id}","${new_point_id}")'
						>
							Next point
						</button>
						`
						element.insertAdjacentElement("afterend", newElement);
						const videos_container = document.createElement('span');
						videos_container.innerHTML = html_videos;
						document.getElementById('AI_window_chat_id').appendChild(videos_container)
						document.getElementById('AI_window_chat_id').appendChild(scriptElement);
						utility.write(`AI_text_introduction_${new_tag}`, html_content)
						setTimeout(
							function(){
								document.getElementById(`buttons_container_${new_tag}`).innerHTML += next_button;
							}, 7500
						);
					}else{
					}

				}, 1000);
			}
		}
	}
	//add new spec moduel
	C_cancel_ask(ask_item_id) {
		const element = document.getElementById(ask_item_id);
		element.remove();
	}
}









util = new util();
view = new view();
Controller = new controller(util, view);
