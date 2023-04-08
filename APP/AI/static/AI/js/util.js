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
}
