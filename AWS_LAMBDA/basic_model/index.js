import OpenAI from 'openai';
//left to figure out the delivery, database update and safety + security measures.


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
      if (functions || function_call) {
        requestOptions.functions = functions;
        requestOptions.function_call = function_call;
      }
      const response = await openai.chat.completions.create(requestOptions);

      var content = "";
      responseStream.setContentType("text/plain");
      for await (const chunk of response) {
		console.log(JSON.stringify(chunk));
		if (function_call){
			if (chunk.choices[0].delta.hasOwnProperty("function_call")){
				responseStream.write(chunk.choices[0].delta.function_call.arguments);
				content += chunk.choices[0].delta.function_call.arguments;
			}else{
				responseStream.end();
				return;
				break;
			}
		}else{
			if (chunk.choices[0].delta.hasOwnProperty("content")){
				responseStream.write(chunk.choices[0].delta.content);
				content += chunk.choices[0].delta.content;
			}else{
				responseStream.end();
				return;
				break;
			}
		}
      }
      responseStream.end();
      console.log(content);
      return;
    } catch (error) {
      // Handle errors here and potentially send an error response
      console.error(error);
    }
  }
);

