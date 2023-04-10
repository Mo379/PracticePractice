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
	M_open_lesson(url, csrf_token, lesson_id, chapter) {
		//opening the port using xhttp
		this.open_port(url);
		this.xhttp.setRequestHeader("X-CSRFToken", csrf_token);    
		//prepairing query
		var query = 'lesson_id=' + lesson_id + '&chapter=' + chapter;
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
	C_open_lesson(url, lesson_id, chapter, csrf_token, modal_name) {
		//send command
		// Get a reference to the modal element
		this.M_open_lesson(url, csrf_token, lesson_id, chapter);

		//make the user wait for the response
		this.view.alert_load_lesson();
		const modal = document.getElementById(modal_name);
		// Close the modal
		$(modal).modal('hide');
		//listen for the repsponse from the server script
		var util = this.util;
		this.xhttp.onreadystatechange = function () {
			if (this.readyState == 4 && this.status == 200) {
				var txt = this.responseText;
				var json = JSON.parse(txt);
				setTimeout(function (){
					var s = document.getElementById('main_chat_scroll_container');
					if (json.error == 0){
						var introduction = false
						if (json.hasOwnProperty("introduction")) {
							introduction = json.introduction
						}
						var chat_html = util.unwrapChat(json.chat, introduction);
						s.innerHTML = chat_html[0]; 
						if (chat_html[1] == true){
							util.write(chat_html[2], chat_html[3]);
						}
						util.scrollToBottom('AI_window_chat_id', 1500); 
					}else{
						s.innerHTML = util.AI_window_error(json.message); 
					}

				}, 1000);
			}
		}
	}
}









util = new util();
view = new view();
controller = new controller(util, view);
