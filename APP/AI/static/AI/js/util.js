class util{
	scrollToBottom(divId, duration) {
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

	unwrapChat(chat) {
		var html = 'Some html';
		return html + chat;
	}
	write(elemID, text, delay_lower=50, delay_higher=120, char_lower=3, char_higher=10) {
	  let element = document.getElementById(elemID);
	  let i = 0;
	  function type() {
	    let charCount = Math.floor(Math.random() * (char_higher - char_lower + 1)) + char_lower;
	    let delay = Math.floor(Math.random() * (delay_higher - delay_lower + 1)) + delay_lower;
	    
	    let shouldPause = Math.random() < 0.1;
	    if (shouldPause) {
	      delay += 100;
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
