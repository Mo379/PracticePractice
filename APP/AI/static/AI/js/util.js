class util{

	AI_window_error(message){
		var element = '<button id="loading_spinner" type="button" disabled><i class="bi bi-exclamation-diamond text-danger"></i><br>'+message+'</button>';
		return element;
	}
	scrollToBottom(divId, duration=1500) {
	//this.util._scrollToBottom('AI_window_chat_id', 1500); 
	  const div = document.getElementById(divId);
	  const scrollTop = div.scrollTop;
	  const scrollHeight = div.scrollHeight;
	  const distance = scrollHeight - scrollTop;
	  const startTime = Date.now();
	  
	  function easeInOutQuad(t, b, c, d) {
	    t /= d / 2;
	    if (t < 1) return c / 2 * t * t + b;
	    t--;
	    return -c / 2 * (t * (t - 2) - 1) + b;
	  }
	  
	  function scroll() {
	    const currentTime = Date.now();
	    const time = Math.min(1, (currentTime - startTime) / duration);
	    const ease = easeInOutQuad(time, 0, 1, 1);
	    div.scrollTop = scrollTop + (distance * ease);
	    if (time < 1) requestAnimationFrame(scroll);
	  }
	  
	  requestAnimationFrame(scroll);
	}


	createChatTextHtml(who, input, textId) {
		var blinker = '';
		var image = 'bi bi-send-fill';
		if (who == 'ai'){
			blinker = `<span class='blink' style='display:inline-block;width: 5px;height:12px;background:var(--text-color-1);'></span>`;
			image = 'bi bi-robot';
		}
		return `<div class='AI_chat_text AI_text_${who}'>
			    <div class='AI_text_wrap'>
			      <div class='AI_text_image'>
				<i class="${image}"></i>
			      </div>
			      <div class='AI_text_text' id='${textId}'>
			      ${blinker}
			      ${input}
			      </div>
			    </div>
			  </div>`;
	}

	unwrapChat(chat, introduction) {
		var output = "";
		var live = false;
		var element = '';
		var text = '';
		//
		if (introduction === false){
		}else{
			output += this.createChatTextHtml('ai', '', 'AI_text_introduction');
			live = true;
			element = 'AI_text_introduction';
			text += introduction;
		}
		return [output, live, element, text]
	}
	write(elemID, text, delay_lower=50, delay_higher=90, char_lower=6, char_higher=10) {
	  let element = document.getElementById(elemID);
	  let i = 0;
	  function type() {
	    let charCount = Math.floor(Math.random() * (char_higher - char_lower + 1)) + char_lower;
	    let delay = Math.floor(Math.random() * (delay_higher - delay_lower + 1)) + delay_lower;
	    
	    let shouldPause = Math.random() < 0.1;
	    if (shouldPause) {
	      delay += 50;
	    }
	    if (i < text.length) {
	      element.innerHTML += text.slice(i, i + charCount);
	      i += charCount;
	      setTimeout(type, delay);
	    }
	  }

	  type();
	}
}
