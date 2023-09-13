import OpenAI from 'openai';
//left to figure out the delivery, database update and safety + security measures.


//
function return_to_app_endpoint(function_app_endpoint, ai_response, ai_function_call){
	try {
		const returnUrl = function_app_endpoint.return_url;
		// Create an object containing all variables to be sent
		var postData = {
			...function_app_endpoint,
			'ai_response': ai_response,
		};
		var ai_function_name = null;
		if (ai_function_call){
			ai_function_name = ai_function_call.name;
		}
		postData = {
			...postData,
			'function_name': ai_function_name,
		};
		//
		var XMLHttpRequest = require('xhr2');
		const xhttp = new XMLHttpRequest();
		xhttp.open('POST', returnUrl, true);
		xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
		xhttp.setRequestHeader("X-CSRFToken", function_app_endpoint.csrf_token);
		xhttp.send(JSON.stringify(postData));
		xhttp.onreadystatechange = function () {
			if (this.readyState == 4 && this.status == 200) {
				console.log(this.status);
			}else{
				console.log(this.status);
			}
		};
		console.log(postData);
	} catch (error){
		// Handle errors here and potentially send an error response
		console.error(error);
	}
}
//
const openai = new OpenAI({
	organization: process.env.OPEN_AI_ORGANISATION,
	apiKey: process.env.OPEN_AI_API_KEY
});
/* global awslambda */
export const handler = awslambda.streamifyResponse(
  async (event, responseStream, _context) => {
    try {
      const body = event.body;
      const messages = JSON.parse(body).message;
      const functions = JSON.parse(body).functions;
      const function_call = JSON.parse(body).function_call;
      const function_app_endpoint = JSON.parse(body).function_app_endpoint;
      console.log(messages);
      console.log(functions);
      console.log(function_call);
      console.log(function_app_endpoint);
      const requestOptions = {
        model: "gpt-3.5-turbo-0613",
        temperature: 0.1,
        messages: messages,
        stream: true,
      };
      if (functions && function_call) {
        requestOptions.functions = functions;
        requestOptions.function_call = function_call;
      }
      const response = await openai.chat.completions.create(requestOptions);

      var content = "";
      responseStream.setContentType("text/plain");
      for await (const chunk of response) {
		if (function_call){
			if (chunk.choices[0].delta.hasOwnProperty("function_call")){
				responseStream.write(chunk.choices[0].delta.function_call.arguments);
				content += chunk.choices[0].delta.function_call.arguments;
			}else{
				responseStream.end();
				console.log(content);
				return_to_app_endpoint(function_app_endpoint, content, function_call);
				return;
				break;
			}
		}else{
			if (chunk.choices[0].delta.hasOwnProperty("content")){
				responseStream.write(chunk.choices[0].delta.content);
				content += chunk.choices[0].delta.content;
			}else{
				responseStream.end();
				console.log(content);
				return_to_app_endpoint(function_app_endpoint, content, function_call);
				return;
				break;
			}
		}
      }
      //
      responseStream.end();
      return;
    } catch (error) {
      // Handle errors here and potentially send an error response
      console.error(error);
    }
  }
);

